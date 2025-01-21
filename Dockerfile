FROM public.ecr.aws/lambda/python:3.10

ARG APPNAME

COPY ./dist/ltrim-0.1.0-py3-none-any.whl ${LAMBDA_TASK_ROOT}/ltrim-0.1.0-py3-none-any.whl

COPY serverless-examples/examples/${APPNAME}/ ${LAMBDA_TASK_ROOT}/

RUN yum update -y

# Get the EPEL repository
RUN yum install -y https://archives.fedoraproject.org/pub/archive/epel/7/x86_64/Packages/e/epel-release-7-14.noarch.rpm \
    && yum install -y epel-release \
    && yum install -y git

RUN pip install -r requirements.txt

RUN pip install ltrim-0.1.0-py3-none-any.whl

RUN echo "PS1='\e[92m\u\e[0m@\e[94m\h\e[0m:\e[35m\w\e[0m# '" >> /root/.bashrc

ENTRYPOINT ["/bin/bash"]
