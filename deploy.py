import json
import boto3
import io
import mimetypes
import operator
import os
import sys
import time
import zipfile

# avoid:
# botocore.errorfactory.ResourceConflictException:
#   An error occurred (ResourceConflictException) when calling the
#   UpdateFunctionCode operation: The operation cannot be performed at this time.
#   An update is in progress for resource: <arn_of_resource>
BLIND_CONFIG_WAIT_TIME = 1.5


'''
invalid_file_top_message = (
"""file %s has an invalid file top!\n\n%s
All python files should start with:
# API_GATEWAY <gateway_id>
# <METHOD> </path>
# LAMBDA <lambda_name>
"""
)

files = os.listdir()
paths = []
for filename in files:
    if os.path.isfile(filename) and filename.endswith(".py") and filename != "deploy.py":
        line_top = ""
        with open(filename) as f:
            for i, line in enumerate(f):
                line_top += line
                if i >= 2:
                    break
        path = {"file": filename}
        for i, line in enumerate(line_top.split("\n")):
            if i >= 3:
                break
            split_line = line.split()
            assert split_line[0] == "#", invalid_file_top_message % (filename, line_top)
            if i == 0:
                assert split_line[1] == "API_GATEWAY", invalid_file_top_message % (filename, line_top)
                path["api_gateway"] = split_line[2]
            elif i == 1:
                path["method"] = split_line[1]
                path["path"] = split_line[2]
            if i == 2:
                assert split_line[1] == "LAMBDA", invalid_file_top_message % (filename, line_top)
                path["lambda"] = split_line[2]
        paths.append(path)

print(json.dumps(paths, indent=4))

gateway_paths = {}
for path in paths:
    method = path["method"]
    path_text = path["path"]
    if path_text not in gateway_paths:
        gateway_paths[path_text] = {}
    gateway_paths[path_text].update({
        method.lower(): {
            "produces": [
                "application/json"
            ],
            "x-amazon-apigateway-integration": {
                "uri": (
                    f"arn:aws:apigateway:{aws_region}:lambda:path/2015-03-31/functions/"
                    f"arn:aws:lambda:{aws_region}:{aws_account_id}:function:"
                    f"{path['lambda']}/invocations"
                ),
                "passthroughBehavior": "when_no_match",
                "httpMethod": "POST", # Note, POST required even for get
                "contentHandling": "CONVERT_TO_TEXT",
                "type": "aws_proxy"
            }
        }
    })

# Get rest_api_id from paths
api_gateway_names = set()
for path in paths:
    api_gateway_names.add(path["api_gateway"])
if len(api_gateway_names) > 1:
    raise Exception(
        f"You specified multiple different API gateways, which is not yet supported!"
        f" Gateways found: {api_gateway_names}"
    )
rest_api_id = api_gateway_names.pop()

# TODO customize name as well
api_name = "killerfrog-api-demo"

api_gateway_json = {
    "swagger": "2.0",
    "info": {
        "version": "2018-07-21T19:28:58Z", # TODO Investigate
        "title": api_name
    },
    "host": f"{rest_api_id}.execute-api.{aws_region}.amazonaws.com",
    "basePath": "/dev",
    "schemes": [
        "https"
    ],
}

api_gateway_json["paths"] = gateway_paths
'''

def deploy_api_gateway(api_gateway_json):
    api_gateway = session.client("apigateway")
    api_gateway.put_rest_api(
        restApiId=rest_api_id,
        mode='overwrite',
        failOnWarnings=True,
        body=json.dumps(api_gateway_json)
    )

    api_gateway.create_deployment(
        restApiId=rest_api_id,
        stageName='dev',
        #stageDescription='string',
        #description='string',
    )
'''
if paths:
    deploy_api_gateway(api_gateway_json)
'''

def aws_python_version():
    info = sys.version_info
    return f"python{info[0]}.{info[1]}"

def create_lambda_layer(lambda_client, layer_name, dependencies):
    """
    dependencies can be a string requirements filename
    or list of dependencies to install
    """
    # WARNING The max size for uploading via bytes is 250MB unzipped,
    # 50MB zipped. Reminder ZipFile by default is uncompressed, need to
    # specify a compression algorithm
    # You will get an error like:
    # botocore.exceptions.SSLError: SSL validation failed for https://lambda.us-east-2.amazonaws.com/2018-10-31/layers/ServerScope_pinger_us-east-2_layer/versions
    # EOF occurred in violation of protocol (_ssl.c:2426)
    os.system("mkdir /tmp/jkassman_lambda_layer_package")
    target_dir = (
        "/tmp/jkassman_lambda_layer_package/"
        f"python/lib/{aws_python_version()}/site-packages/"
    )
    os.system(f"mkdir -p {target_dir}")

    if isinstance(dependencies, str):
        # Assume we were given a requirements file
        os.system(f"pip install -r {dependencies} --target={target_dir}")
    else:
        for dependency in dependencies:
            os.system(
                f"pip install --target={target_dir} {dependency}"
            )

    print(f"Installed dependencies to {target_dir}")

    zipped_bytes = io.BytesIO()
    cwd = os.getcwd()
    os.chdir("/tmp/jkassman_lambda_layer_package")
    with zipfile.ZipFile(zipped_bytes, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for subdir, dirs, files in os.walk("./"): #/tmp/jkassman_lambda_layer_package"):
            for file in files:
                z.write(os.path.join(subdir, file))
    os.chdir(cwd)


    response = lambda_client.publish_layer_version(
        LayerName=layer_name,
        Content={"ZipFile": zipped_bytes.getvalue()},
        CompatibleRuntimes=[aws_python_version()]
    )
    os.system("rm -r /tmp/jkassman_lambda_layer_package/")

    version_arn = response["LayerVersionArn"]
    print(f"Created '{version_arn}'")
    return version_arn


def lookup_latest_layer_arn(lambda_client, layer_name):
    response = lambda_client.list_layer_versions(
        LayerName=layer_name,
        CompatibleRuntime=aws_python_version(),
        MaxItems=50,
    )
    if "NextMarker" in response:
        raise Exception("Too lazy to deal with pagination, delete some layers plz")
    versions = response["LayerVersions"]
    versions.sort(key=operator.itemgetter("Version"), reverse=True)

    return versions[0]["LayerVersionArn"]

def create_lambda(
    client,
    lambda_name,
    lambda_file,
    lambda_timeout_s=None,
    iam_role="midway_lambda",
    principal='apigateway.amazonaws.com',
    source_arn=None,
    zipped_bytes=None,
    dependencies=None,
    lambda_layer_arn=None,
):
    if dependencies and not lambda_layer_arn:
        lambda_layer_arn = create_lambda_layer(
            lambda_client,
            lambda_name + "_layer",
            dependencies,
        )

    if lambda_layer_arn == "lookup_latest":
        lambda_layer_arn = lookup_latest_layer_arn(client, lambda_name + "_layer")

    if zipped_bytes is None:
        zipped_bytes = io.BytesIO()
        with zipfile.ZipFile(zipped_bytes, "w") as z:
            z.write(lambda_file)

    config = dict(
        FunctionName=lambda_name,
        Role=f"arn:aws:iam::{aws_account_id}:role/{iam_role}",
        Handler=f'{os.path.splitext(lambda_file)[0]}.lambda_handler',
        #Description='string',
        #Timeout=123,
        #MemorySize=123,
      )
    if lambda_timeout_s:
        config["Timeout"] = lambda_timeout_s
    if lambda_layer_arn:
        config["Layers"] = [lambda_layer_arn]
    try:
      client.create_function(
        Runtime=aws_python_version(),
        Code={"ZipFile": zipped_bytes.getvalue()},
        **config,
      )
    except client.exceptions.ResourceConflictException:
        if args.force_updates:
            client.update_function_configuration(**config)
            time.sleep(BLIND_CONFIG_WAIT_TIME)
        client.update_function_code(
            FunctionName=lambda_name,
            ZipFile=zipped_bytes.getvalue()
        )
    if args.force_updates and source_arn:
        statement_id = f'{lambda_name}-policy'
        try:
            client.remove_permission(
                FunctionName=lambda_name,
                StatementId=statement_id,
                #Qualifier='string',
                #RevisionId='string'
            )
        except client.exceptions.ResourceNotFoundException:
            pass
        time.sleep(BLIND_CONFIG_WAIT_TIME)
        client.add_permission(
            FunctionName=lambda_name,
            StatementId=statement_id,
            Action='lambda:InvokeFunction',
            Principal=principal,
            SourceArn=source_arn
            #SourceAccount='string',
            #EventSourceToken='string',
            #Qualifier='string',
            #RevisionId='string',
            #PrincipalOrgID='string',
            #FunctionUrlAuthType='NONE'|'AWS_IAM'
        )

'''
lambda_client = session.client("lambda")

for path in paths:
    api_source_arn =  (
        f"arn:aws:execute-api:{aws_region}:{aws_account_id}:{rest_api_id}"
        f"/*/{path['method'].upper()}{path['path']}"
    )
    create_lambda(lambda_client, path["lambda"], path["file"], api_source_arn)
'''

def deploy_s3_files():
    s3 = session.client("s3")
    home_page = ""
    with open("s3_list.txt") as f:
        for i, line in enumerate(f):
            split_line = line.split()
            if i == 0:
                assert split_line[0] == "S3_BUCKET:"
                bucket_name = split_line[1]
            else:
                if len(split_line) == 2:
                    assert split_line[1] == "#HOMEPAGE"
                    home_page = split_line[0]
                else:
                    assert len(split_line) == 1, split_line
                file_name_to_upload = split_line[0]
                s3.upload_file(
                    file_name_to_upload, bucket_name, file_name_to_upload,
                    ExtraArgs={
                        "ACL":"public-read",
                        "ContentType": mimetypes.guess_type(file_name_to_upload)[0]
                    }
                )

    print(f"https://{bucket_name}.s3.{aws_region}.amazonaws.com/{home_page}")

#deploy_s3_files()
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--force_updates', action="store_true")
    args = parser.parse_args()

    # Set this up manually with `aws configure`
    session = boto3.session.Session()
    aws_region = session.region_name
    aws_account_id = session.client("sts").get_caller_identity()["Account"]

    print(aws_region)

    files_to_deploy = [
        "lambda_handler.py",
        "connector.py",
        "location_utils.py",
        "Ping_Gathering/ping_saver.py",
        "passwords/lamb_ping_insert_password.txt",
    ]

    zipped_bytes = io.BytesIO()
    with zipfile.ZipFile(zipped_bytes, "w") as z:
        for filename in files_to_deploy:
            z.write(filename)

    lambda_client = session.client("lambda")
    create_lambda(
        client=lambda_client,
        lambda_name="ServerScope_pinger_us-east-2",
        lambda_file="lambda_handler.py",
        lambda_timeout_s=120,
        iam_role="AWSLambdaBasicExecutionRole",
        principal=None, # cloudwatch?
        source_arn=None,
        zipped_bytes=zipped_bytes,
        #dependencies="reqirements.txt",
        #dependencies=["tcppinglib", "requests", "cachetools", "mysql-connector-python"], # exclude matplotlib
        #lambda_layer_arn=f"arn:aws:lambda:us-east-2:{aws_account_id}:layer:ServerScope_pinger_us-east-2_layer:16",
        lambda_layer_arn="lookup_latest"
    )
