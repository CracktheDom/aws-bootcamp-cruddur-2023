# Week 3 — Decentralized Authentication
## Create Cognito User Pool
#### Use AWS CLI
```bash
aws cognito-idp create-user-pool --pool-name cruddur_pool \
--policies PasswordPolicy={MinimumLength=16} \
--schema Name=first_name,AttributeDataType=String,Required=True \
--schema Name=last_name,AttributeDataType=String,Required=True \
--schema Name=preferred_username,AttributeDataType=String,Required=True \
--deletion-protection ACTIVE \
--auto-verified-attributes email \
--username-attributes email \
--mfa-configuration OFF \
--user-attribute-update-settings AttributesRequireVerificationBeforeUpdate=email \
--admin-create-user-config AllowAdminCreateUserOnly=false \
--username-configuration CaseSensitive=True \
--account-recovery-setting "RecoveryMechanisms=[{Priority=1,Name="verified_email"}]"
```
![HINT: pic of AWS CLI showing JSON response]()
#### Navigate to AWS Cognito to Create Client App
* On the **cruddur_pool** User Pool info page, click on the **App integration** tab

![HINT: pic of user pool info page]()
* Navigate down to **App client list** section
* Click on **Create app client** button
* Ensure **Public client** is selected for the **App type**
* Enter a name in the **App client name** field
* Finally click on the **Create app client** button
* On the **cruddur_pool** info page, click the **App integration** tab and navigate down to **App client list** section
* Copy the **Client ID** to **REACT_APP_AWS_USER_POOLS_WEB_CLIENT_ID** environment variable in the `docker-compose.yml` file

![HINT pic of user pool web client id]()
#### Add aws-amplify to frontend
* Navigate to `frontend-react-js` directory and execute `npm install aws-amplify --save`
* Verify `aws-amplify` is in the `frontend-react-js/package.json` file
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

* Navigate to `frontend-react-js/src/pages/SigninPage.js` and remove the cookie import statement & append the file with the following code:

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
#### Run Containers to check if implementation of aws-amplify is working
* In a terminal, execute `docker compose -f "docker-compose.yml" up -d --build`
* Click on URL to the frontend, click on **Sign In** button, enter email and password, on **Sign In** button
* **Incorrect username or password** error message should pop up

![HINT: pic of error message displayed on Sign In page()

#### Go to AWS Cognito Console and create a new user

