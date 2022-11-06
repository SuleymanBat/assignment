#!/usr/bin/env python3

import troposphere.ec2 as ec2
from troposphere import Ref, Template, Tags, GetAtt
from troposphere.ec2 import Route, VPCGatewayAttachment, SubnetRouteTableAssociation, \
            Subnet, RouteTable, VPC, SubnetNetworkAclAssociation, EIP, InternetGateway

#Generate a CloudFormation template that creates a VPC for the AWS accounts (Growth-Dev, Growth-Stage, Growth-Prod)
#user input requests
is_valid = True
while is_valid == True:
    input_account_user = input('Account (ex.: Growth-Dev, Growth-Stage, Growth-Prod): ')
    input_account = input_account_user.lower()
    if input_account == "growth-dev" or input_account == "growth-stage" or input_account == "growth-prod":
        is_valid = False
    else:
        print("INVALID ENTRY: PLEASE CHOOSE ONLY AMONG Growth-Dev, Growth-Stage, Growth-Prod")
        is_valid = True
if input_account == "growth-dev":
    DnsHostnames = "false"
else:
    DnsHostnames = "true"

input_tag = input_account_user
input_aws_region = input('AWS region (ex.: us-east-1): ')
if input_account == "growth-dev":
    input_vpc_cidr = "10.0.0.0/24"
elif input_account == "growth-stage":
    input_vpc_cidr = "10.1.0.0/18"
else:
    input_vpc_cidr = "10.2.0.0/18"
input_pub_az_amount = int(input('In how many different AZs you want to create PUBLIC subnets? (max. 3): '))
input_pri_az_amount = int(input('In how many different AZs you want to create PRIVATE subnets? (max. 3): '))
input_pro_az_amount = int(input('In how many different AZs you want to create PROTECTED subnets? (max. 3): '))

# Create the object that will generate our template
t = Template()
t.set_version('2010-09-09')
t.set_description('AWS CloudFormation VPC Custom Template')

ref_stack_id = Ref('AWS::StackId')
ref_region = Ref('AWS::Region')
ref_stack_name = Ref('AWS::StackName')

#Create VPC
VPC = t.add_resource(
    VPC(
        'VPC',
        EnableDnsSupport="true",
        EnableDnsHostnames=DnsHostnames,
        CidrBlock=input_vpc_cidr,
        Tags=Tags(
            Application=ref_stack_id,
            Name=input_tag+'-vpc'
            )))
#Our VPC will need internet access:      
#Create Internet Gateway
internetGateway = t.add_resource(
    InternetGateway(
        'InternetGateway',
        Tags=Tags(
            Application=ref_stack_id,
            Name=input_tag+'-ig'
            )))
#Attach Internet Gateway to the VPC
gatewayAttachment = t.add_resource(
    VPCGatewayAttachment(
        'AttachGateway',
        VpcId=Ref(VPC),
        InternetGatewayId=Ref(internetGateway)))
        # Notice how you can't attach an IGW to a VPC unless both are created.

#Create Main Public RouteTable has direct routing to IGW
MainRouteTable = t.add_resource(
    RouteTable(
        'MainRouteTable',
        VpcId=Ref(VPC),
        Tags=Tags(
            Application=ref_stack_id,
            Name=input_tag+'-PublicRouteTable-Main'
            )))
#Create route 0.0.0.0/0 in the Public RouteTable
route = t.add_resource(
    Route(
        'Route',
        DependsOn='AttachGateway',
        GatewayId=Ref('InternetGateway'),
        DestinationCidrBlock='0.0.0.0/0',
        RouteTableId=Ref(MainRouteTable),
    ))

#Create Public Subnets and associated with MainRouteTable
#This LOOP will provide the CIDR values used by the subnets
for i in range(input_pub_az_amount):
    # Determine CIDR for each Public Subnet
    if i == 0:
        AZ = input_aws_region+'a'
        if input_account == "growth-dev": input_pub_subnet_cidr = "10.0.0."+str(i+1)+"/27"
        elif input_account == "growth-stage": input_pub_subnet_cidr = "10.1."+str(i+1)+".0/24"
        else: input_pub_subnet_cidr = "10.2."+str(i+1)+".0/24"
    elif i == 1:
        AZ = input_aws_region+'b'
        if input_account == "growth-dev": input_pub_subnet_cidr = "10.0.0."+str(i*32+1)+"/27"
        elif input_account == "growth-stage": input_pub_subnet_cidr = "10.1."+str(i*7)+".0/24"
        else: input_pub_subnet_cidr = "10.2."+str(i*7)+".0/24"
    elif i == 2:
        AZ = input_aws_region+'c'
        if input_account == "growth-dev": input_pub_subnet_cidr = "10.0.0."+str(i*32+1)+"/27"
        elif input_account == "growth-stage": input_pub_subnet_cidr = "10.1."+str(i*7)+".0/24"
        else: input_pub_subnet_cidr = "10.2."+str(i*7)+".0/24"
    #Create Public Subnet(s)
    #input_number_of_public_subnets = int(input('How many PUBLIC subnets in ' + AZ + ' AZ you need?: ')) #user input request
    input_number_of_public_subnets = 1
    while input_number_of_public_subnets > 0:
        subnet_logical_id = 'PubSubnet' + str(input_number_of_public_subnets) + AZ.replace("-", "")
        input_number_of_public_subnets -= 1
        # Create Public Subnet
        pub_subnet = t.add_resource(
        Subnet(
            subnet_logical_id,
            CidrBlock=input_pub_subnet_cidr,
            VpcId=Ref(VPC),
            AvailabilityZone=AZ,
            Tags=Tags(
                Application=ref_stack_id,
                Name=input_tag + '-' + subnet_logical_id
                )))

        #Create RouteTable Association (MAIN)
        UniqueSubnetRouteTableAssociation = 'SubnetRouteTableAssociation' + subnet_logical_id
        subnetRouteTableAssociation = t.add_resource(
        SubnetRouteTableAssociation(
        UniqueSubnetRouteTableAssociation,
           SubnetId=Ref(pub_subnet),
            RouteTableId=Ref(MainRouteTable),
        ))

#Create Private RouteTable
PrivateRouteTableName = 'PrivateRouteTable' #+ subnet_logical_id
PrivateRouteTable = t.add_resource(
    RouteTable(
        PrivateRouteTableName,
        VpcId=Ref(VPC),
        Tags=Tags(
            Application=ref_stack_id,
            Name=input_tag+'-'+PrivateRouteTableName
            )))

#Create Private Subnets and associated with PrivateRouteTable
for i in range(input_pri_az_amount):
    # Determine CIDR for each Private Subnet
    if i == 0:
        AZ = input_aws_region+'a'
        if input_account == "growth-dev": input_pri_subnet_cidr = "10.0.0."+str(i*32+97)+"/27"
        elif input_account == "growth-stage": input_pri_subnet_cidr = "10.1."+str(i+21)+".0/24"
        else: input_pri_subnet_cidr = "10.2."+str(i+21)+".0/24"
    elif i == 1:
        AZ = input_aws_region+'b'
        if input_account == "growth-dev": input_pri_subnet_cidr = "10.0.0."+str(i*32+97)+"/27"
        elif input_account == "growth-stage": input_pri_subnet_cidr = "10.1."+str((i*7)+21)+".0/24"
        else: input_pri_subnet_cidr = "10.2."+str((i*7)+21)+".0/24"
    elif i == 2:
        AZ = input_aws_region+'c'
        if input_account == "growth-dev": input_pri_subnet_cidr = "10.0.0."+str(i*32+97)+"/27"
        elif input_account == "growth-stage": input_pri_subnet_cidr = "10.1."+str((i*7)+21)+".0/24"
        else: input_pri_subnet_cidr = "10.2."+str((i*7)+21)+".0/24"
    #Create Private Subnet
    #input_number_of_private_subnets = int(input('How many PRIVATE subnets in ' + AZ + ' AZ you need?: ')) #user input request
    input_number_of_private_subnets = 1
    while input_number_of_private_subnets > 0:
        subnet_logical_id = 'PriSubnet' + str(input_number_of_private_subnets) + AZ.replace("-", "")
        input_number_of_private_subnets -= 1
        # Create Private Subnet
        pri_subnet = t.add_resource(
        Subnet(
            subnet_logical_id,
            CidrBlock=input_pri_subnet_cidr,
            VpcId=Ref(VPC),
            AvailabilityZone=AZ,
            Tags=Tags(
                Application=ref_stack_id,
                Name=input_tag + '-' + subnet_logical_id
                )))
        #Create RouteTable Association for each private subnet
        #Attach the private subnets to private route tables:
        UniqueSubnetRouteTableAssociation = 'SubnetRouteTableAssociation' + subnet_logical_id
        subnetRouteTableAssociation = t.add_resource(
        SubnetRouteTableAssociation(
            UniqueSubnetRouteTableAssociation,
            SubnetId=Ref(pri_subnet),
            RouteTableId=Ref(PrivateRouteTable),
        ))

#Create NAT Gateway for protected subnet(s)
#Allocate EIP
UniqueNatEipName = 'NatEip' + AZ.replace("-", "")
nat_eip = t.add_resource(ec2.EIP(
UniqueNatEipName,
Domain="vpc",
))
#Create NAT Gateway
UniqueNatGatewayName = 'NAT' + AZ.replace("-", "")
nat = t.add_resource(ec2.NatGateway(
UniqueNatGatewayName,
AllocationId=GetAtt(nat_eip, 'AllocationId'),
SubnetId=Ref(pub_subnet),
Tags=Tags(
Application=ref_stack_id,
Name=input_tag + '-' + UniqueNatGatewayName
)))

#Create Protected RouteTable
ProtectedRouteTableName = 'ProtectedRouteTable' #+ subnet_logical_id
ProtectedRouteTable = t.add_resource(
    RouteTable(
        ProtectedRouteTableName,
        VpcId=Ref(VPC),
        Tags=Tags(
            Application=ref_stack_id,
            Name=input_tag+'-'+ProtectedRouteTableName
            )))
#Create default route 0.0.0.0/0 in the Protected RouteTable
Protected_route = t.add_resource(
    Route(
        'ProtectedRoute',
        DestinationCidrBlock='0.0.0.0/0',
        NatGatewayId=Ref(UniqueNatGatewayName),
        RouteTableId=Ref(ProtectedRouteTable),
    ))

#Create Protected Subnets associated with ProtectedRouteTable & NAT 
for i in range(input_pro_az_amount):
    # Determine CIDR for each Private Subnet
    if i == 0:
        AZ = input_aws_region+'a'
        if input_account == "growth-dev": input_pro_subnet_cidr = "10.0.0."+str(i*32+193)+"/27"
        elif input_account == "growth-stage": input_pro_subnet_cidr = "10.1."+str(i+42)+".0/24"
        else: input_pro_subnet_cidr = "10.2."+str((i*7)+42)+".0/24"
    elif i == 1:
        AZ = input_aws_region+'b'
        if input_account == "growth-dev": input_pro_subnet_cidr = "10.0.0."+str(i*32+193)+"/28"
        elif input_account == "growth-stage": input_pro_subnet_cidr = "10.1."+str((i*7)+42)+".0/24"
        else: input_pro_subnet_cidr = "10.2."+str((i*7)+42)+".0/24"
    elif i == 2:
        AZ = input_aws_region+'c'
        if input_account == "growth-dev": input_pro_subnet_cidr = "10.0.0."+str(i*24+193)+"/28"
        elif input_account == "growth-stage": input_pro_subnet_cidr = "10.1."+str((i*7)+42)+".0/24"
        else: input_pro_subnet_cidr = "10.2."+str(i+1)+".0/24"
    #Create Protected Subnet(s)
    #input_number_of_protected_subnets = int(input('How many PROTECTED subnets in ' + AZ + ' AZ you need?: ')) #user input request
    input_number_of_protected_subnets = 1
    while input_number_of_protected_subnets > 0:
        subnet_logical_id = 'ProSubnet' + str(input_number_of_protected_subnets) + AZ.replace("-", "")
        input_number_of_protected_subnets -= 1
        # Create Protected Subnet
        pro_subnet = t.add_resource(
        Subnet(
            subnet_logical_id,
            CidrBlock=input_pro_subnet_cidr,
            VpcId=Ref(VPC),
            AvailabilityZone=AZ,
            Tags=Tags(
                Application=ref_stack_id,
                Name=input_tag + '-' + subnet_logical_id
                )))
        #Create RouteTable Association for each protected subnet
        UniqueSubnetRouteTableAssociation = 'SubnetRouteTableAssociation' + subnet_logical_id
        subnetRouteTableAssociation = t.add_resource(
        SubnetRouteTableAssociation(
            UniqueSubnetRouteTableAssociation,
            SubnetId=Ref(pro_subnet),
            RouteTableId=Ref(ProtectedRouteTable),
        ))
# Finally, write the template to a file
with open('solution.yaml', 'w') as f:
    f.write(t.to_yaml())

print('---YAML-CF-TEMPLATE-START----\n')
print(t.to_yaml())
print('---YAML-CF-TEMPLATE-END----')
