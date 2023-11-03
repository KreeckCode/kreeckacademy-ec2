# Hello Mweb

<h3> Hope everyone is having a good day, please view the video link for the test on this link <b> https://youtu.be/afBKQTvd_Is </b> </h3>

# Technologies used.
<hr>
<h3> Python Based </h3>
<li> Django Rest Framework - API </li>
<li> Django - Backend</li>
<li> Tailwind CSS</li>
  
<h3> Cloud Based</h3>
<li> AWS S3 - for Static and Media File storage</li>
<li> AWS EC2 - for virtual computing</li>
<li> AWS Cloudfront - for the content delivery</li>
<li> AWS RDS - for the static files delivery</li>
<li> AWS VPC</li>


# Why I didn’t go for AWS Lambda
1.	AWS Lambda is Function as a Service. The unit of hosting is a function rather than an application. These functions need to be stateless and short-running.
2.	So, if we need to host an application in Lambda, we need to break the app into the stateless short-running functions and then if required, tie them together.
3.	Ease of migration of existing web app to Function as a Service depends on how much the architecture of application matches to the Function as a Service requirements.
4.	Please note that Function as a Service is not meant for all use cases. So, migration needs to be thought only if the use case fitment is there.

Drawbacks

5.	Limited runtime environment: AWS Lambda has a limited runtime environment, which means that you may need to make some modifications to your Django site in order to run it on AWS Lambda.
6.	Cold start issues: When a new instance of my Django application is launched on AWS Lambda, it may experience a "cold start" issue where the initial request takes longer to process. This can be a problem for sites that receive a lot of traffic, as it could result in slower response times for your users.
7.	Limited control over the hosting environment: Because AWS Lambda manages the hosting environment for the Django site, i have limited control over the underlying infrastructure. This can make it more difficult to troubleshoot issues or customize your setup.


