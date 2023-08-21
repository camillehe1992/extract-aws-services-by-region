BASE := $(shell /bin/pwd)
TF ?= terraform
AWS ?= aws
PIP ?= pip
MAKE ?= make

export AWS_PROFILE=210692783429_UserFull

target:
	$(info ${HELP_MESSAGE})
	@exit 0

create-stack:
	$(info [*] Create Infrastructure using AWS CLI)
	@$(AWS) cloudformation create-stack --stack-name terraform-infrastructure --template-body file://cloudformation/tf_infrastructure.yaml

install:
	$(info [*] Installing pipenv project dependencies)
	@$(PIP) install -r requirements-dev.txt

init:
	$(info [*] Terraform Init)
	@$(TF) init -reconfigure

package:
	$(info [*] Install Function Packages)
	rm -rf build/
	mkdir build/
	cp -r extract-services-by-region ./build/
	pip install -r ./build/extract-services-by-region/requirements.txt --target ./build/extract-services-by-region/
plan:
	$(info [*] Terraform Plan )
	@$(MAKE) package
	@$(TF) plan -out tfplan

apply:
	$(info [*] Terraform Apply )
	@$(TF) apply -auto-approve tfplan

deploy:
	@$(MAKE) init
	@$(MAKE) plan
	@$(MAKE) apply

destroy:
	@$(MAKE) init
	@$(TF) plan -destroy -out tfplan
	@$(MAKE) apply

#############
#  Helpers  #
#############


define HELP_MESSAGE
	Environment variables to be aware of or to hardcode depending on your use case:

	Common usage:

	...::: Terraform Init :::...
	$ make init

    ...::: Terraform Plan :::...	
    $ make plan

    ...::: Terraform Apply :::...
	$ make apply

	...::: Terraform Init, Plan, and Apply :::...
	$ make deploy

	...::: Terraform Apply an Destroy Plan :::...
	$ make destroy
endef