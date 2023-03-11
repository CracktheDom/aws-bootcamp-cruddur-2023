# Week 3 — Decentralized Authentication
## Create Cognito User Pool
#### Use AWS CLI
```bash
aws cognito-idp create-user-pool --pool-name cruddur --policies PasswordPolicy={MinimumLength=16} \
--deletion-protection ACTIVE --auto-verified-attributes=email --username-attributes email \
--mfa-configuration OFF --user-attribute-update-settings AttributesRequireVerificationBeforeUpdate="email" \
--admin-create-user-config AllowAdminCreateUserOnly=false \
--account-recovery-setting RecoveryMechanisms=[{"Priority": 1, "Name": "verified_email"}]
```
#### Add aws-amplify to frontend
* Navigate to `frontend-react-js` directory and execute `npm install aws-amplify --save`
* Verify `aws-amplify` is in the `frontend-react-js/package.json` file
* Navigate to `frontend-react-js/src/App.js` and append the file with the following code:

```js
import { Amplify } from 'aws-amplify'; 
...

Amplify.configure({
  "AWS_PROJECT_REGION": process.env.REACT_APP_AWS_PROJECT_REGION,
  "aws_cognito_identity_pool_id": process.env.REACT_APP_AWS_COGNITO_ID,
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
