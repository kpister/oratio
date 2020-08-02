Create AWS account. Get Security Access Keys from security info page

Run
```
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```
Check with `aws` to see if the install succeeded.
Run `aws configure` to begin configuration.
Set Access key and secret key
Optionally set us-west-2 and json as the other parameters
