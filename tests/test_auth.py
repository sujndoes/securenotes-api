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
