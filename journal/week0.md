# Week 0 — Billing and Architecture

### Videos
##### Livestream
- *Dumb Questions*
- Iron Triangle
##### Security Considerations
- Least Privilege
#### IAM
* created a new IAM user and attached Administrator permission policy
* generated programmatic credentials
#### Billing
* created a $1 USD monthly AWS Budget 
* ![Image of CLI output of Zero Spend budget](/assets/Screenshot_20230217_171543.png)

& a monthly $1 USD credit spend budget
```sh
$ aws budgets describe-budget --budget-name "My Monthly Credit Spend" --account-id $(aws sts get-caller-identity --query Account --output text)
```
```yaml
Budget:
  BudgetLimit:
    Amount: '1.0'
    Unit: USD
  BudgetName: My Monthly Credit Spend
  BudgetType: COST
  CalculatedSpend:
    ActualSpend:
      Amount: '0.0'
      Unit: USD
    ForecastedSpend:
      Amount: '0.034'
      Unit: USD
  CostFilters: {}
  CostTypes:
    IncludeCredit: true
    IncludeDiscount: false
    IncludeOtherSubscription: false
    IncludeRecurring: false
    IncludeRefund: false
    IncludeSubscription: true
    IncludeSupport: false
    IncludeTax: false
    IncludeUpfront: false
    UseAmortized: false
    UseBlended: false
  LastUpdatedTime: '2023-02-17T18:02:22.669000-06:00'
  TimePeriod:
    End: '2087-06-14T19:00:00-05:00'
    Start: '2023-01-31T18:00:00-06:00'
  TimeUnit: MONTHLY
```
* created Billing Alarm via Account Settings & CloudWatch
```sh
$ aws cloudwatch describe-alarms
```
```yaml
CompositeAlarms: []
MetricAlarms:
- ActionsEnabled: true
  AlarmActions:
  - arn:aws:sns:us-east-2:785139023983:Default_CloudWatch_Alarms_Topic
  AlarmArn: arn:aws:cloudwatch:us-east-2:785139023983:alarm:BillingAlarmist
  AlarmConfigurationUpdatedTimestamp: '2023-02-18T06:13:38.837000+00:00'
  AlarmName: BillingAlarmist
  ComparisonOperator: GreaterThanOrEqualToThreshold
  DatapointsToAlarm: 1
  Dimensions:
  - Name: Currency
    Value: USD
  EvaluationPeriods: 1
  InsufficientDataActions: []
  MetricName: EstimatedCharges
  Namespace: AWS/Billing
  OKActions: []
  Period: 21600
  StateReason: 'Unchecked: Initial alarm creation'
  StateTransitionedTimestamp: '2023-02-18T06:13:38.837000+00:00'
  StateUpdatedTimestamp: '2023-02-18T06:13:38.837000+00:00'
  StateValue: INSUFFICIENT_DATA
  Statistic: Maximum
  Threshold: 1.0
  TreatMissingData: missing
```
#### Gitpod CDE
* configured Github repo to be writable, so that Gitpod can sync changes to Github
* installed AWS CLI v2 in gitpod CDE & added commands in gitpod.yml file to install AWS CLI v2
* created AWS environment variables for AWS region, access key, secret access key & account ID so that they presist restarts of the CDE
* AWS CLI installed correctly on Gitpod and successfully called aws sts get-caller-identity
![Image of AWS CLI installation and successful API call](/assets/Screenshot_20230217_220823.png)
#### Conceptual & Architectural Diagrams
![Image of conceptual diagram](/assets/Conceptual_Architecture.drawio-V2.svg)
![Image of conceptual napkin diagram](/assets/IMG_20230218_105509723.jpg)
