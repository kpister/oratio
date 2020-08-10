## AWS Setup

Create AWS account. Get Security Access Keys from security info page and follow the below commands.

#### Setup Run on OS::Mac
```
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```
Check with `aws` to see if the install succeeded.
- Run `aws configure` to begin configuration.
- Set Access key and secret key
- Optionally set us-west-2 and json as the other parameters


#### Setup Run on OS::Linux x86(64bit)

This area portrays how to install the AWS CLI version 2 on Linux. The AWS CLI version 2 has no dependencies on other Python packages. It has a self-contained, embedded copy of Python included in the installer.
```
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```
(Optional) Downloading from the URL - o download the installer with your browser, use the following URL: Click [(Download here)](https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip). You can verify the integrity and authenticity of your downloaded installation file before you extract (unzip) the package.

Confirm your installation
```
aws --version
```
Check with `aws` to see if the install succeeded.
- Run `aws configure` to begin configuration.
- Set Access key and secret key
- Optionally set us-west-2/east-2 and json as the other parameters
