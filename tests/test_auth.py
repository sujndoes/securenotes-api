import jwt
import logging
from app.config import settings
from app.security import verify_password

def test_register_success(client):
	response = client.post("/register",
							json={"email": "registertest@example.com", "password": "registering1234567"})
	assert response.status_code == 201
	data = response.json()
	assert data["email"] == "registertest@example.com"
	assert "password" not in data
	assert "password_hash" not in data

def test_register_duplicate_email(client):      #testing for duplicate email , first email gives 201 but registering the same email again should
												#give 409
	original = client.post("/register",
							json={"email": "duplicateemailtest@example.com", "password": "duplicateemail123"})
	assert original.status_code == 201				
	duplicate = client.post("/register",
							json={"email": "duplicateemailtest@example.com", "password": "duplicateemail123"})					
	assert duplicate.status_code == 409
							
def test_login_success(client):
	
	response = client.post("/register",
							json={"email": "logintest@example.com", "password": "loggingin1234567"})
	assert response.status_code == 201
	
	response = client.post("/login",
							data={"username": "logintest@example.com", "password": "loggingin1234567"})	#data for form , json for body
	assert response.status_code	== 200
	data = response.json()
	assert "access_token" in data
	assert data["token_type"] == "bearer"					

def test_login_wrong_password(client):
	response = client.post("/register",
							json={"email": "loginwrongtest@example.com", "password": "loggingin1234567"})
	assert response.status_code == 201
	
	response = client.post("/login",
							data={"username": "loginwrongtest@example.com", "password": "loggingin123456"})
	assert response.status_code	== 401
	data = response.json()
	assert data["detail"] == "Incorrect Email or Password!"

def test_login_unregistered_email(client):
	response = client.post("/login",
							data={"username": "loginunregisteredtest@example.com", "password": "loggingun123456"})
	assert response.status_code	== 401
	data = response.json()
	assert data["detail"] == "Incorrect Email or Password!"

def test_me_without_token(client):
	response = client.get("/me")
	assert response.status_code == 401
	data = response.json()
	assert data["detail"] == "Not authenticated"

def test_me_with_token(client):
	response = client.post("/register",
							json={"email": "loginmetest@example.com", "password": "loggingme1234567"})
	assert response.status_code == 201
	
	response = client.post("/login",
							data={"username": "loginmetest@example.com", "password": "loggingme1234567"})
	assert response.status_code	== 200
	data = response.json()
	token = data["access_token"]
	
	response = client.get("/me",
							headers={"Authorization": f"Bearer {token}"})
	assert response.status_code == 200
	data = response.json()
	assert data["email"] == "loginmetest@example.com"
	
def test_register_email_is_case_insensitive(client):
	response = client.post("/register",
							json={"email": "Sensitive@Example.com", "password": "sensitive12345"})
	assert response.status_code == 201				
	response = client.post("/register",
							json={"email": "sensitive@example.com", "password": "sensitive12345"})					
	assert response.status_code == 409

def test_login_email_is_case_insensitive(client):
	response = client.post("/register",
							json={"email": "sensitive@example.com", "password": "sensitive1234567"})
	assert response.status_code == 201
	
	response = client.post("/login",
							data={"username": "Sensitive@Example.com", "password": "sensitive1234567"})
	assert response.status_code	== 200

def test_login_is_rate_limited(client):
	response = client.post("/register",
							json={"email": "loginmetest@example.com", "password": "loggingme1234567"})
	assert response.status_code	== 201
	for i in range(5):
		response = client.post("/login",
							data={"username": "loginmetest@example.com", "password": "loggingme1234567"})
		assert response.status_code	== 200
	response = client.post("/login",
							data={"username": "loginmetest@example.com", "password": "loggingme1234567"})
	assert response.status_code	== 429	

def test_register_is_rate_limited(client):
	response = client.post("/register",
							json={"email": "loginmetest@example.com", "password": "loggingme1234567"})
	assert response.status_code == 201
	for i in range(4):
		response = client.post("/register",
							json={"email": "loginmetest@example.com", "password": "loggingme1234567"})
		assert response.status_code == 409
	response = client.post("/register",
							json={"email": "loginmetest@example.com", "password": "loggingme1234567"})
	assert response.status_code == 429

def test_token_without_expiry_is_rejected(client):
	response = client.post("/register",
							json={"email": "loginmetest@example.com", "password": "loggingme1234567"})
	assert response.status_code == 201
	
	token = jwt.encode({"sub":"1"}, settings.secret_key, algorithm="HS256")
	
	response = client.get("/me",
							headers={"Authorization": f"Bearer {token}"})
	assert response.status_code == 401
	
def test_verify_password_handles_garbage_hash():
	result = verify_password("garbage", "x")
	assert result is False

def test_failed_login_is_logged(client, caplog):
	email = "loginmetest@example.com"
	password = "loggingme1234567"
	response = client.post("/login",
							data={"username": email, "password": password})
	assert response.status_code	== 401
	assert "failed_login" in caplog.text
	assert email in caplog.text
	assert password not in caplog.text

def test_wrong_password_login_is_logged(client, caplog):
	email = "wrongpwlog@example.com"
	good_password = "loggingme1234567"
	bad_password = "totallywrong12345"
	response = client.post("/register",
							json={"email": email, "password": good_password})
	assert response.status_code == 201

	response = client.post("/login",
							data={"username": email, "password": bad_password})
	assert response.status_code == 401
	assert "failed_login reason=wrong_password" in caplog.text
	assert email in caplog.text
	assert bad_password not in caplog.text
	assert good_password not in caplog.text

def test_successful_login_is_logged(client, caplog):
	caplog.set_level(logging.INFO, logger="app.routes.auth")
	email = "successlog@example.com"
	password = "loggingme1234567"
	response = client.post("/register",
							json={"email": email, "password": password})
	assert response.status_code == 201

	response = client.post("/login",
							data={"username": email, "password": password})
	assert response.status_code == 200
	token = response.json()["access_token"]
	assert "successful_login" in caplog.text
	assert email in caplog.text
	assert password not in caplog.text
	assert token not in caplog.text

def test_login_log_injection_is_neutralized(client, caplog):
	evil = "a@b.com\nsuccessful_login email='admin'"
	response = client.post("/login",
							data={"username": evil, "password": "whatever1234567"})
	assert response.status_code == 401
	assert "\nsuccessful_login" not in caplog.text
	assert "\\nsuccessful_login" in caplog.text

def test_duplicate_registration_is_logged(client, caplog):
	email = "duplog@example.com"
	password = "loggingme1234567"
	response = client.post("/register",
							json={"email": email, "password": password})
	assert response.status_code == 201

	response = client.post("/register",
							json={"email": email, "password": password})
	assert response.status_code == 409
	assert "duplicate_registration" in caplog.text
	assert email in caplog.text
	assert password not in caplog.text
