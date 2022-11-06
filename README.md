

This python script genaretes Cloudformation templates using troposphere.

In order to run the scripts run the following commands:
pip install troposphere

python app.py


Troposphere kutuphanesi kullanilarak  'Growth-Dev', 'Growth-Stage', 'Growth-Prod' isimlerinde uc ayri VPC olusturubilecek python scripti yazildi.
Bu application calisirken interactive oldugu icin kullanicidan bazi bilgiler almasi gerekiyor. 
Bu script, assignment da istenen hangi tur VPC sinin olusturulacagi bu VPC sinin hangi AWS region inda olacagi, kac Availability Zone da kurulacagi, her bir AZ icin Private, Public ve Protected Subnet den kacar adet olacagi gibi bilgilerin interactive olarak girilmesi gerekir.  

Bu bilgileri girerek istenilen region da assignment da belirtilen VPC turlerinin herhangi birinde istenen sayida AZ de custom template olusturulabilir.
Proof of concept olmasi icin bu script kullanilarak bir template olusturuldu. Bu template ile;
Assignment da gecen 'Growth-Dev' accountu icin us-east-1 region da iki AZ de bir VPC, 
bu VPC icerisinde her bir AZ icin CIDR blocklari assignment da belirtilen sekilde bir Private Subnet, bir Public Subnet, bir Protected subnet olusturuldu.
Olusturulan template i validation icin Cloud formation da denendi. Olusturulan mimari asagidaki gibidir.


In the public subnet of each availability zone, which is attached directly to a Internet Gateway, and a NAT Gateway for the protected subnet in the availability zone. There is also set up for EIP and Routing Tables within this subnet which is used for effectively routing the protected subnet's data.


The use of the NAT Gateway ensures that the outside world cannot get into anything inside the protected subnet, but the protected subnet can talk to the outside world, traffic for the protected subnet can first hit the NAT and pass it on depending on the security rules of the NAT gateway itself.

(template.png)




Assignment
The Growth team has created 3 new AWS accounts (Growth-Dev, Growth-Stage, Growth-Prod)
and would like you to develop a solution to create Cloudformation templates that set-up some
base infrastructure.
Some considerations:
● They may want to use the same tool to add additional accounts in the future.
● How you might test/validate your generated templates.
They have requested that the tool initially creates templates for the accounts as follows:
● Each account should have a VPC with
○ Dev:
■ VPC IP: 10.0.0.0
■ Netmask: 255.255.255.0
■ DNS Support enabled
■ Default instance tenancy
○ Stage:
■ VPC IP: 10.1.0.0
■ Netmask: 255.255.192.0
■ DNS Support and DNS Hostnames enabled
■ Default instance tenancy
○ Prod:
■ VPC IP: 10.2.0.0
■ Netmask: 255.255.192.0
■ DNS Support and DNS Hostnames enabled
■ Default instance tenancy

● Each account should have the following multi-az subnets. The VPC IPs should be
spread as evenly as possible between the az’s.
○ Private:
■ No internet access
○ Public
■ Outbound internet access
○ Protected
■ Outbound internet access via NAT

● Tags should be added to each resource for billing purposes. You may decide which tags
to add.


