import boto3
import io
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:807771583695:deployPortfolioTopic')

    try:
        s3 = boto3.resource('s3')

        portfolio_bucket = s3.Bucket('www.moabouissa.com')
        build_bucket = s3.Bucket('build.moabouissa.com')

        portfolio_zip = io.BytesIO()
        build_bucket.download_fileobj('buildportfolio.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        print('Job Successful')
        topic.publish(Subject="Successfully Updated Portfolio", Message="You have successfully updated your portfolio")
    except:
        topic.publish(Subject="Portfolio Deployment Failed", Message="Your portfolio deployment has failed")
        raise
    return 'Hello from Lambda'