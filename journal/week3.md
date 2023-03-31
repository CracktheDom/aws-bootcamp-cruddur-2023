# Week 3 — Decentralized Authentication
## Create Cognito User Pool
### Use AWS CLI
```sh
aws cognito-idp create-user-pool --pool-name cruddur_poolhall \
--policies PasswordPolicy={MinimumLength=16,RequireUppercase=True,RequireLowercase=True,RequireNumbers=True} \
--schema Name=full_name,AttributeDataType=String,Required=True,Mutable=True \
--schema Name=preferred_username,AttributeDataType=String,Required=True,Mutable=True \
--deletion-protection ACTIVE \
--auto-verified-attributes email \
--username-attributes email \
--mfa-configuration OFF \
--user-attribute-update-settings AttributesRequireVerificationBeforeUpdate=email \
--admin-create-user-config AllowAdminCreateUserOnly=false \
--username-configuration CaseSensitive=True \
--email-configuration  \
--account-recovery-setting "RecoveryMechanisms=[{Priority=1,Name="verified_email"}]"
```
![HINT: pic of AWS CLI showing JSON response](https://user-images.githubusercontent.com/85846263/229114307-c3ae46bd-8c84-468e-b9b4-ca719c610eb1.png)

### Navigate to AWS Cognito to Create Client App
* On the ***cruddur_pool*** User Pool info page, click on the ***App integration*** tab

![HINT: pic of user pool info page](https://user-images.githubusercontent.com/85846263/229114518-eed57288-ec62-46cb-8860-067ef9a28990.png)
* Navigate down to ***App client list*** section
* Click on ***Create app client*** button
* Ensure ***Public client*** is selected for the ***App type***
* Enter a name in the ***App client name*** field
* Finally click on the ***Create app client*** button
* On the ***cruddur_pool*** info page, click the ***App integration*** tab and navigate down to ***App client list*** section
* Copy the ***Client ID*** to ***REACT_APP_AWS_USER_POOLS_WEB_CLIENT_ID*** environment variable in the `docker-compose.yml` file

![HINT pic of user pool web client id](https://user-images.githubusercontent.com/85846263/229114730-56811879-f398-449f-8080-c878894bf830.png)
### Add aws-amplify to frontend
* Navigate to `frontend-react-js` directory and execute `npm install aws-amplify --save`
* Verify ***aws-amplify*** is in the `frontend-react-js/package.json` file
* Navigate to `frontend-react-js/src/App.js` and append the file with the following code:

```js
import { Amplify } from 'aws-amplify'; 
...

Amplify.configure({
  "AWS_PROJECT_REGION": process.env.REACT_APP_AWS_PROJECT_REGION,
  "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
  "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
  "aws_user_pools_web_client_id": process.env.REACT_APP_AWS_USER_POOLS_WEB_CLIENT_ID,
  "oauth": {},
  Auth: {
    // We are not using an Identity Pool
    // identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID, // REQUIRED - Amazon Cognito Identity Pool ID
    region: process.env.REACT_APP_AWS_PROJECT_REGION,              // REQUIRED - Amazon Cognito Region
    userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,        // OPTIONAL - Amazon Cognito User Pool ID
    userPoolWebClientId: process.env.REACT_APP_AWS_USER_POOLS_WEB_CLIENT_ID,  // OPTIONAL - Amazon Cognito 
  }
})
```
* added the relevant amplify environment variables to `docker-compose.yml` file

```yaml
  frontend-react-js:
    environment:
      REACT_APP_AWS_PROJECT_REGION: "${AWS_DEFAULT_REGION}"
      REACT_APP_AWS_COGNITO_ID: "*"
      REACT_APP_AWS_COGNITO_REGION: "${AWS_DEFAULT_REGION}"
      REACT_APP_AWS_USER_POOLS_ID: "us-east-2_fjgjtuh"  # User Pool ID
      REACT_APP_CLIENT_ID: "76ytuhju980kiojly934fdgp"
```
#### Conditionally show components based on whether user is logged in or not
* Navigate to `frontend-react-js/src/pages/HomeFeedPage.js` and append the file with the following code:

```js
import { Amplify } from 'aws-amplify'; 
...

  const checkAuth = async () => {
    console.log('checkAuth')
    // [TODO] Authenication
    Auth.currentAuthenicatedUser({
      // Optional, By default is false.
      // If set to true, this call will send a 
      // request to Cognito to get the latest user data
      bypassCache: false
    })
    .then((user) => {
      console.log('user', user);
      return Auth.currentAuthenticatedUser()
    }).then((cognito_user) => {
      setUser({
        display_name: cognito_user.attributes.name,
        handle: cognito_user.attributes.preferred_username
      })
    })
    .catch((err) => console.log(err));
  };
```
discuss which sections of frontend will be displayed or hidden when user logs in

* Next, in the `frontend-react-js/src/components/ProfileInfo.js` file, add import statement & replace the code block that contains cookie with the following code:

```js
import { Amplify } from 'aws-amplify'; 
...

  const signOut = async () => {
    try {
        await Auth.signOut({ global: true });
        window.location.href = "/"
    } catch (error) {
      console.log('error signing out: ', error);
    }
  }
```

* Navigate to `frontend-react-js/src/pages/SigninPage.js` and remove the ***cookie*** import statement & append the file with the following code:

```js
import { Auth } from 'aws-amplify';
...

  const onsubmit = async (event) => {
    event.preventDefault();
    setErrors('')
    try {
      Auth.signIn(email, password)
        .then(user => {
          localStorage.setItem("access_token", user.signInUserSession.accessToken.jwtToken)
          window.location.href = "/"                               
        })
        .catch(err => { console.log('Error!', err) });
    } catch (error) {
      if (error.code == 'UserNotConfirmedException') {
        window.location.href = "/confirm"
      }
      setErrors(error.message)
    }
    return false
  }
```
### Run Containers to check if implementation of aws-amplify is working
* In a terminal, execute `docker compose -f "docker-compose.yml" up -d --build`
* Click on URL to the frontend, click on ***Sign In*** button, enter email and password, on ***Sign In*** button
* ***Incorrect username or password*** error message should pop up

![HINT: pic of error message displayed on Sign In page](https://user-images.githubusercontent.com/85846263/229115603-78f64ec9-018f-4245-9cd1-05744e378916.png)

### Go to AWS Cognito Console and Manually Create a New User
* Click on ***Create user*** button
* Enter email address and password and check the box for ***Mark email address as verified***
* Click on ***Create user*** button

### Go to Cruddur Sign In Page
* Sign in the with same credentials used on the Cognito ***Create user*** page
I received a "user Session is null" error, when I look at the user info for the newly created user, the page displayed the "Force Password Change" under the Email verified section, but the app has not been fully implemented to utilize password changes, so I executed the following command in a terminal:

```sh
aws cognito-idp admin-set-user-password \
--user-pool-id us-east-2_7cm4Q6fHv \
--username <email_address> \
--password <new_password> \
--permanent
```
* With the email now verified, go to Cruddur (frontend url), sign in successfully

![HINT pic showing successfully logged into Cruddur after manually creating user](https://user-images.githubusercontent.com/85846263/229115787-373b72e2-0c9e-4a37-9353-cd4ba3555935.png)

### Implement aws-amplify in SignupPage.js, ConfirmationPage.js and RecoverPage.js
#### SignupPage.js
* Enter insert the import statement into `frontend-react-js/src/pages/SignupPage.js` and replace ***onsubmit*** variable with following code:

```js
import { Auth } from 'aws-amplify'
...

  const onsubmit = async (event) => {
    event.preventDefault();
    setErrors('');
    try {
      const { user } = await Auth.signUp({
        username: email,
        password: password,
        attributes: {
          name: name,
          email: email,
          preferred_username: username,
        },
        autoSignIn: { // optional - enables auto sign in after user is confirmed
          enabled: true,
        }
      });
      console.log('user', user);
      window.location.href = `/confirm?email=$(email)`
    } catch (error) {
      console.log(error);
      setErrors(error.message)
    }
    return false
  }
```
#### ConfirmationPage.js
* Enter insert the import statement into `frontend-react-js/src/pages/ConfirmationPage.js` and replace ***resend_code*** and ***onsubmit*** variables with following code:
```js
import { Auth } from 'aws-amplify'
...

  const resend_code = async (event) => {
    console.log('resend_code')
    // [TODO] Authenication
    setErrors('')
    try{
      await Auth.resentSignUp(email);
      console.log('code resent successfully');
      setCodeSent(true)
    } catch (err) {
      console.log(err)
      if (err.message == 'Username cannot be empty'){
        setErrors('You need to provide email in order to send Resent Activation Code')
      } else if (err.message == 'Username/client id combination not found.') {
        setErrors('Email is invalid or cannot be found.')
      }
    }
  }
  
  const onsubmit = async (event) => {
    event.preventDefault();
    console.log('ConfirmationPage.onsubmit')
    // [TODO] Authenication
   try {
    await Auth.confirmSingUp(email, code);
     window.location.href = '/'
   } catch (error) {
    setErrors(error.message)
   }  
```

#### RecoverPage.js
* Enter insert the import statement into `frontend-react-js/src/pages/RecoverPage.js` and replace ***onsubmit_send_code*** and ***onsubmit_confirm_code*** variables with following code:
```js
  const onsubmit_send_code = async (event) => {
    event.preventDefault();
    console.log('onsubmit_send_code')
    setErrors('')
    Auth.forgotPassword(username)
    .then((data) => setFormState('confirm_code'))
    .catch(err) => setErrors(err.message));    
    return false
  }

  const onsubmit_confirm_code = async (event) => {
    event.preventDefault();
    console.log('onsubmit_confirm_code')
    setErrors('')
    if (password == passwordAgain){
      Auth.forgotPasswordSubmit(username, code, password)
      .then((data) => setFormState('success'))
      .catch((err) => setCognitoErrors(err.message));
    } else {
      setCognitoErrors('Passwords do not match')
    }
    return false
  }
```
### Test Account Creation via the Cruddur site
* Go to Cognito and delete the manually created user
* Go to Cruddur site (frontend) and click the ***Join Now*** button
* Enter all relevant info and click ***Sign In***
* Cognito will show the newly user, but show that email has not been verified

![Pic of newly created user but email has not been verified](https://user-images.githubusercontent.com/85846263/229116279-63ddd465-4ed8-4fdd-8cac-b392cfd61399.png)
* On the ***Confirm Your Email*** page, enter email and confirmation code that was mailed to the same email address and click ***Confirm Email*** button
* Cognito will show confirmed status of user

![Pic of confirmation page](https://user-images.githubusercontent.com/85846263/229116451-2c683b0d-2544-43cc-9810-50a14380ba8d.png)

### Test Password Recovery
* Logout of Cruddur site and click on ***Forgot Password*** link
* Enter email address and a email with a confirmation code will be sent to the provided email address
* On the ***Recovery your Password***, enter confirmation code and new password twice, click on ***Reset Password***

![HINT: pic of recovery page](https://user-images.githubusercontent.com/85846263/229116563-d27e81c3-6ea8-4968-823a-6b997fc7bd99.png)

* Successful password reset will be displayed

![hint pic of password reset](https://user-images.githubusercontent.com/85846263/229116724-79a7b8f2-1dde-4a49-8535-5d867def07bf.png)
* Log back in with new credentials to verify that new password works

![HINT: pic of successful lgoin after reset](https://user-images.githubusercontent.com/85846263/229116821-2169ba4f-c382-456e-b14b-3441ab21340b.png)

## Implement handling of JSON Web Token (JWT) in the backend
* Add *python-jose* and *Flask-AWSCognito* to `backend-flask/requirements.txt`
* Execute `python3 -m pip install -r backend-flask/requirement.txt` to install dependencies
* Execute `python3 -m pip freeze > backend-flask/requirements.txt` to add version numbers to packages
* Create new directory named `lib` in `backend-flask` directory by executing:

```sh 
mkdir backend-flask/lib 
```
* Create new Python file `touch backend-flask/lib/cognito_token_verification.py`
* Insert following code into `backend-flask/lib/cognito_token_verification.py`

```py
import time
import requests
from jose import jwt, jwk
from jose.exceptions import JOSEError
from jose.utils import base64url_decode


class FlaskAWSCognitoError(Exception):
    pass


class TokenVerifyError(Exception):
    pass


class TokenService:
    def __init__(self, user_pool_id, user_pool_client_id, region, request_client=None):
        self.region = region
        if not self.region:
            raise FlaskAWSCognitoError("No AWS region provided")
        self.user_pool_id = user_pool_id
        self.user_pool_client_id = user_pool_client_id
        self.claims = None
        if not request_client:
            self.request_client = requests.get
        else:
            self.request_client = request.client
        self._load_jwk_keys()


    def _load_jwk_keys(self):
        keys_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
        try:
            response = self.request_client(keys_url)
            self.jwk_keys = response.json()["keys"]
        except requests.exceptions.RequestException as e:
            raise FlaskAWSCognitoError(str(e)) from e


    @staticmethod
    def _extract_headers(token):
        try:
            headers = jwt.get_unverified_headers(token)
            return headers
        except JOSEError as e:
            raise TokenVerifyError(str(e)) from e


    def _find_pkey(self, headers):
        kid = headers["kid"]
        # search for the kid in the downloaded public keys
        key_index = -1
        for index, _ in enumerate(self.jwk_keys):
            if kid == self.jwk_keys[index]["kid"]:
                key_index = index
                break
        if key_index == -1:
            raise TokenVerifyError("Public key not found in jwks.json")
        return self.jwk_keys[key_index]

    @staticmethod
    def _verify_signature(token, pkey_data):
        try:
            # construct the public key
            public_key = jwk.construct(pkey_data)
        except JOSEError as e:
            raise TokenVerifyError(str(e)) from e
        # get the last two sections of the token, message and signature (base64 encoded)
        message, encoded_signature = str(token).rsplit(".", 1)

        # decode the signature
        decode_signature = base64url_decode(encoded_signature.encode("utf-8"))

        # verify the signature
        if not public_key.verify(message.encode("utf-8"), decode_signature):
            raise TokenVerifyError("Signature verification failed")


    @staticmethod
    def _extract_claims(token):
        try:
            claims = jwt.get_unverified_claims(token)
            return claims
        except JOSEError as e:
            raise TokenVerifyError(str(e)) from e


    @staticmethod
    def _check_expiration(claims, current_time):
        if not current_time:
            current_time = time.time()
        if current_time > claims['exp']:
            raise TokenVerifyError('Token is expired')  # probably another exception


    def _check_audience(self, claims):
        # and the Audience (use claims['client_id'] if verifying an access token)
        audience = claims['aud'] if 'aud' in claims else claims['client_id']
        if audience != self.user_pool_client_id:
            raise TokenVerifyError("Token was not issued for this audience")


    def verify(self, token, current_time=None):
        """ https://github.com/awslabs/aws-support-tools/blob/master/Cognito/decode-verify-jwt/decode-verify-jwt.py """
        if not token:
            raise TokenVerifyError("No token provided")

        headers = self._extract_headers(token)
        pkey_data = self._find_pkey(headers)
        self._verify_signature(token, pkey_data)

        claims = self._extract_claims(token)
        self._check_expiration(claims, current_time)
        self._check_audience(claims)

        self.claims = claims


    def extract_access_token(self, request_headers):
        access_token = None
        auth_header = request_headers.get("Authorization")
        if auth_header and " " in auth_header:
            _, access_token = auth_header.split()
        return access_token
```
* Update backend-flask/app.py

```py
# ---FlaskAWSCognito JWT service ---
from lib.cognito_token_verification import TokenService
...

# ---FlaskAWSCognito JWT service ---
cognitoTokenService = TokenService(
  user_pool_id=os.getenv("AWS_COGNITO_USER_POOL_ID"), 
  user_pool_client_id=os.getenv("AWS_COGNITO_USER_POOL_CLIENT_ID"), 
  region=os.getenv("AWS_DEFAULT_REGION")
)

@app.route("/api/activities/home", methods=['GET'])
@cross_origin()
def data_home():
  access_token = TokenService.extract_access_token(request.headers)

  try:
    cognitoTokenService.token_service.verify(access_token)
  except TokenVerifyError as e:
    _ = request.data
    abort(make_response(jsonify(message=str(e)), 401))

  data = HomeActivities.run()
  return data, 200
```
* Add Cognito environmental variables to `docker-compose.yml`

```yml
services:
  backend-flask:
    environment:
      FRONTEND_URL: "http://3000-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
      BACKEND_URL: "http://4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}"
      OTEL_SERVICE_NAME: 'backend-flask'
      AWS_COGNITO_USER_POOL_ID: <user pool id>
      AWS_COGNITO_USER_POOL_CLIENT_ID: <user pool client id>
```
* Run containers and navigate to Cruddur frontend, login to app
