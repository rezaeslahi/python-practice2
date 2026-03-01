import boto3

def discover_boto():
    # print(type(boto3))
    # print(dir(boto3))
    help(boto3.client)

if __name__ == "__main__":
    print("Running...")
    discover_boto()
