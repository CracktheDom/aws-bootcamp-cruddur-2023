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
![HINT: pic of AWS CLI showing JSON response]()
### Navigate to AWS Cognito to Create Client App
* On the ***cruddur_pool*** User Pool info page, click on the ***App integration*** tab

![HINT: pic of user pool info page]()
* Navigate down to ***App client list*** section
* Click on ***Create app client*** button
* Ensure ***Public client*** is selected for the ***App type***
* Enter a name in the ***App client name*** field
* Finally click on the ***Create app client*** button
* On the ***cruddur_pool*** info page, click the ***App integration*** tab and navigate down to ***App client list*** section
* Copy the ***Client ID*** to ***REACT_APP_AWS_USER_POOLS_WEB_CLIENT_ID*** environment variable in the `docker-compose.yml` file

![HINT pic of user pool web client id]()
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

![HINT: pic of error message displayed on Sign In page]()

### Go to AWS Cognito Console and Manually Create a New User
* Click on ***Create user*** button
* Enter email address and password and check the box for ***Mark email address as verified***
* Click on ***Create user*** button

### Go to Cruddur Sign In Page
* Sign in the with same credentials used on the Cognito ***Create user*** page
I received a "user Session is null" error, when I look at the user info for the newly created user, the page displayed the "Force Password Change" under the Email verified section, but the app has not been fully implemented to utilize password changes, so exeucted the following command in a terminal:

```sh
aws cognito-idp admin-set-user-password \
--user-pool-id us-east-2_7cm4Q6fHv \
--username <email_address> \
--password <new_password> \
--permanent
```
* With the email now verified, go to Cruddur (frontend url), sign in successfully

![HINT pic showing successfully logged into Cruddur after manually creating user]()

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
* Go to Cognito and delete the maunally created user
* Go to Cruddur site (frontend) and click the ***Join Now*** button
* Enter all relevant info and click ***Sign In***
* Cognito will show the newly user, but show that email has not been verified

![Pic of newly created user but email has not been verified]()
* On the ***Confirm Your Email*** page, enter email and confirmation code that was mailed to the same email address and click ***Confirm Email*** button
* Cognito will show confirmed status of user

![Pic of confirmation page]()

### Test Password Recovery
* Logout of Cruddur site and click on ***Forgot Password*** link
* Enter email address and a email with a confirmation code will be sent to the provided email address
* On the ***Recovery your Password***, enter confirmation code and new password twice, click on ***Reset Password***

![HINT: pic of recovery page]()
* Successful password reset will be displayed

![hint pic of password reset]()
* Log back in with new credentials to verify that new password works

![HINT: pic of successful lgoin after reset]()

## Implement passing of JSON Web Token (JWT)
* hmmm


