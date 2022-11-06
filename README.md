
## This python script genaretes Cloudformation templates using troposphere.

In order to run the scripts run the following commands:

'pip install troposphere'

'python app.py'

A python script was written to create three separate VPCs named 'Growth-Dev', 'Growth-Stage', 'Growth-Prod' using the Troposphere library.

Since this application is interactive while running, it needs to get some information from the user.
In this script, information such as which type of VPC requested in the assignment will be created, which AWS region this VPC will be in, how many Availability Zones it will be installed in, how many Private, Public and Protected Subnets for each AZ should be entered interactively.

By providing this information, in the desired region,
A custom template can be created in the VPC types and AZs specified in the assignment.

A template was created using this script to be a proof of concept. With this template;
One VPC in two AZs in us-east-1 region for the 'Growth-Dev' account mentioned in the Assignment,
Within this VPC, a Private Subnet, a Public Subnet, a Protected subnet have been created for each AZ, with CIDR blocks as specified in the assignment.

The created template was tried in Cloud formation for validation.

In the public subnet of each availability zone, which is attached directly to a Internet Gateway, and a NAT Gateway for the protected subnet in the availability zone. There is also set up for EIP and Routing Tables within this subnet which is used for effectively routing the protected subnet's data.

The use of the NAT Gateway ensures that the outside world cannot get into anything inside the protected subnet, but the protected subnet can talk to the outside world, traffic for the protected subnet can first hit the NAT and pass it on depending on the security rules of the NAT gateway itself.

The created architecture is as follows.

![Template](template.png)


