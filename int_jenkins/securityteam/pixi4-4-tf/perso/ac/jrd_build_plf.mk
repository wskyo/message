#this makefile is defined to build the customized plf file to the target xml file.
#this will be included in the plf's Android.mk
#add by zhongyang.hu 20150308
.PHONY: FORCE

LOCAL_PLF_MODULE := $(strip $(LOCAL_PLF_MODULE))
ifeq ($(LOCAL_PLF_MODULE),)
$(error LOCAL_PLF_MODULE is empty!)
endif

ifneq ($(IS_INDEPENDENT_APP),yes)
PLF_MODULE_DIR := $(strip $(PLF_MODULE_DIR))
ifeq ($(PLF_MODULE_DIR),)
$(error PLF_MODULE_DIR is empty!)
endif
endif

ifeq ($(PLF_GLOBAL_INITIALIZED),)
PLF_GLOBAL_INITIALIZED := true

PLF_MERGE_TOOL := python $(JRD_BUILD_PATH)/common/jrd_update_plf.py
PLF_SOURCE_DIR := $(JRD_CUSTOM_RES)/wimdata/wprocedures/plf
XML_PROCESS_TOOL := python $(JRD_BUILD_PATH)/common/xml-process.py

$(PLF_SOURCE_DIR):
	mkdir -p $@

# PLF_PARSE_TOOL := $(JRD_BUILD_WIMDATA_TOOLS)/prd2xml
# PLF_PROCESS_SYS_TOOL := $(JRD_BUILD_PATH)/common/process_sys_plf.sh

# //// ------------------------------------------------------------
# //// handled by jrd_merge_sys_plf.sh
# PLF_PROP_COMMON_FILE := $(JRD_WIMDATA)/wprocedures/isdm_sys_properties.plf
# PLF_MK_COMMON_FILE := $(JRD_WIMDATA)/wprocedures/isdm_sys_makefile.plf

# PLF_PROP_PROJECT_FILE := $(JRD_WIMDATA)/wprocedures/$(JRD_PROJECT)/isdm_sys_properties.plf
# PLF_MK_PROJECT_FILE := $(JRD_WIMDATA)/wprocedures/$(JRD_PROJECT)/isdm_sys_makefile.plf

# PLF_PROP_SOURCE_FILE := $(JRD_CUSTOM_RES)/wimdata/wprocedures/isdm_sys_properties.plf
# PLF_MK_SOURCE_FILE := $(JRD_CUSTOM_RES)/wimdata/wprocedures/isdm_sys_makefile.plf

# ifneq ($(JRD_PROJECT),)
# ifneq ($(wildcard $(PLF_PROP_PROJECT_FILE)),)
# $(PLF_PROP_SOURCE_FILE): $(PLF_PROP_COMMON_FILE) $(PLF_PROP_PROJECT_FILE) | $(PLF_SOURCE_DIR)
#	$(PLF_MERGE_TOOL) $(PLF_PROP_PROJECT_FILE) $(PLF_PROP_COMMON_FILE) $@
# else
# $(PLF_PROP_SOURCE_FILE): $(PLF_PROP_COMMON_FILE) | $(PLF_SOURCE_DIR) $(ACP)
# 	$(ACP) $< $@
# endif

# ifneq ($(wildcard $(PLF_MK_PROJECT_FILE)),)
# $(PLF_MK_SOURCE_FILE): $(PLF_MK_COMMON_FILE) $(PLF_MK_PROJECT_FILE) | $(PLF_SOURCE_DIR)
#	$(PLF_MERGE_TOOL) $(PLF_MK_PROJECT_FILE) $(PLF_MK_COMMON_FILE) $@
# else
# $(PLF_MK_SOURCE_FILE): $(PLF_MK_COMMON_FILE) | $(PLF_SOURCE_DIR) $(ACP)
#	$(ACP) $< $@
# endif
# else
# PLF_PROP_SOURCE_FILE := $(PLF_PROP_COMMON_FILE)
# PLF_MK_SOURCE_FILE := $(PLF_MK_COMMON_FILE)
# endif

# .PHONY: plf-global-target
# plf-global-target: $(PLF_PROP_SOURCE_FILE) $(PLF_MK_SOURCE_FILE)
#	$(PLF_PROCESS_SYS_TOOL) $(JRD_TOOLS_ARCT) $(PLF_PROP_SOURCE_FILE) $(PLF_MK_SOURCE_FILE) \
#		$(JRD_CUSTOM_RES)
# //\\ ------------------------------------------------------------
endif

PLF_SOURCE_FILE := $(PLF_SOURCE_DIR)/isdm_$(LOCAL_PLF_MODULE).plf

PLF_ORIGINAL_COMMON_FILE := $(JRD_WIMDATA)/wprocedures/plf-base/plf/isdm_$(LOCAL_PLF_MODULE).plf
$(PLF_SOURCE_FILE): PRIVATE_PLF_ORIGINAL_COMMON_FILE := $(PLF_ORIGINAL_COMMON_FILE)

PLF_SOURCE_FILE_RULE_CREATED := false

#######################################################BEGIN 20151024 for task732553 by wuyue.lei
##############################################################################OLD 
#ifneq ($(JRD_PROJECT),)
#PLF_ORIGINAL_PROJECT_FILE := $(JRD_WIMDATA)/wprocedures/$(JRD_PROJECT)/plf/isdm_$(LOCAL_PLF_MODULE).plf
#ifneq ($(wildcard $(PLF_ORIGINAL_PROJECT_FILE)),)
#$(PLF_SOURCE_FILE): PRIVATE_PLF_ORIGINAL_PROJECT_FILE := $(PLF_ORIGINAL_PROJECT_FILE)
#$(PLF_SOURCE_FILE): $(PLF_ORIGINAL_COMMON_FILE) $(PLF_ORIGINAL_PROJECT_FILE) | $(PLF_SOURCE_DIR) FORCE
#	$(PLF_MERGE_TOOL) $(PRIVATE_PLF_ORIGINAL_PROJECT_FILE) $(PRIVATE_PLF_ORIGINAL_COMMON_FILE) $@
#
#PLF_SOURCE_FILE_RULE_CREATED := true
#endif
#endif
#######################################################################################NEW
ifneq ($(JRD_PROJECT),)
PLF_ORIGINAL_PROJECT_FILE := $(JRD_WIMDATA)/wprocedures/$(JRD_PROJECT)/plf/isdm_$(LOCAL_PLF_MODULE).plf
ifneq ($(wildcard $(PLF_ORIGINAL_COMMON_FILE))),)
ifneq ($(wildcard $(PLF_ORIGINAL_PROJECT_FILE)),)


$(PLF_SOURCE_FILE): PRIVATE_PLF_ORIGINAL_PROJECT_FILE := $(PLF_ORIGINAL_PROJECT_FILE)
$(PLF_SOURCE_FILE): $(PLF_ORIGINAL_COMMON_FILE) $(PLF_ORIGINAL_PROJECT_FILE) | $(PLF_SOURCE_DIR) FORCE
	$(PLF_MERGE_TOOL) $(PRIVATE_PLF_ORIGINAL_PROJECT_FILE) $(PRIVATE_PLF_ORIGINAL_COMMON_FILE) $@

else 
$(PLF_SOURCE_FILE): $(PLF_ORIGINAL_COMMON_FILE) | $(PLF_SOURCE_DIR) FORCE
	$(ACP) -fp $< $@
endif
PLF_SOURCE_FILE_RULE_CREATED := true
else
ifneq ($(wildcard $(PLF_ORIGINAL_PROJECT_FILE)),)
$(PLF_SOURCE_FILE):PRIVATE_PLF_ORIGINAL_PROJECT_FILE := $(PLF_ORIGINAL_PROJECT_FILE)
$(PLF_SOURCE_FILE):$(PLF_ORIGINAL_PROJECT_FILE) | $(PLF_SOURCE_DIR) FORCE
	$(ACP) -fp $< $@
else
$(error plf-base>>>$(PLF_ORIGINAL_COMMON_FILE) and project>>>$(PLF_ORIGINAL_PROJECT_FILE) all not exit)
endif
PLF_SOURCE_FILE_RULE_CREATED := true
endif
endif
###################################################################################3END 20151024 for task732553

ifeq ($(PLF_SOURCE_FILE_RULE_CREATED),false)
$(PLF_SOURCE_FILE): $(PLF_ORIGINAL_COMMON_FILE) | $(PLF_SOURCE_DIR) $(ACP) FORCE
	$(ACP) -fp $< $@
endif

ifeq ($(IS_INDEPENDENT_APP),yes)
PLF_TARGET_DIR := $(JRD_OUT_CUSTPACK)/plf/$(LOCAL_PLF_MODULE)
else
PLF_TARGET_DIR := $(JRD_CUSTOM_RES)/$(PLF_MODULE_DIR)/res/values
endif
PLF_TARGET_PREFIX := $(PLF_TARGET_DIR)/isdm_$(LOCAL_PLF_MODULE)
PLF_TARGET_FILE := $(PLF_TARGET_PREFIX)_defaults.xml

$(PLF_TARGET_FILE): PRIVATE_PLF_SOURCE_FILE := $(PLF_SOURCE_FILE)
$(PLF_TARGET_FILE): PRIVATE_PLF_TARGET_DIR := $(PLF_TARGET_DIR)
$(PLF_TARGET_FILE): PRIVATE_PLF_TARGET_PREFIX := $(PLF_TARGET_PREFIX)
$(PLF_TARGET_FILE): PRIVATE_PLF_TARGET_FILE := $(PLF_TARGET_FILE)

$(PLF_TARGET_FILE): $(PLF_SOURCE_FILE)
	@echo "generating file: $(PRIVATE_PLF_TARGET_FILE)"
	mkdir -p $(PRIVATE_PLF_TARGET_DIR)
	$(call transform-module-plf-to-xml,$(PRIVATE_PLF_SOURCE_FILE),$(PRIVATE_PLF_TARGET_DIR))
	rm -f $(PRIVATE_PLF_TARGET_PREFIX)_struct.h
	rm -f $(PRIVATE_PLF_TARGET_PREFIX)_value.h
	rm -f $(PRIVATE_PLF_TARGET_PREFIX)_*.log
	mv $(PRIVATE_PLF_TARGET_PREFIX)_android.xml $(PRIVATE_PLF_TARGET_FILE)

ifeq ($(LOCAL_PLF_MODULE),framework-res)
FRAMEWORK_RES_XML :=$(JRD_CUSTOM_RES)/$(PLF_MODULE_DIR)/res/values/jrd_symbols.xml
$(FRAMEWORK_RES_XML): $(PLF_TARGET_FILE)
	$(warning wuyuelei_XML_PROCESS_TOOL==$(XML_PROCESS_TOOL)___PLF_MERGE_TOOL===$(PLF_MERGE_TOOL))
	$(XML_PROCESS_TOOL) $^ $@
#	$(shell sed -i 's/aaaatype/type/g' $@)
	sed -i 's/aaaatype/type/g' $@
   $(call intermediates-dir-for,APPS,$(LOCAL_PLF_MODULE),,COMMON)/package-export.apk: $(FRAMEWORK_RES_XML)
else
   $(call intermediates-dir-for,APPS,$(LOCAL_PLF_MODULE),,COMMON)/src/R.stamp: $(PLF_TARGET_FILE)
endif

INDEPENDENT_APP_FLAG := $(JRD_CUSTOM_RES)/flag/independent_app_flag
ifeq ($(IS_INDEPENDENT_APP),yes)
$(INDEPENDENT_APP_FLAG) : $(PLF_TARGET_FILE)
endif
$(INDEPENDENT_APP_FLAG) :
	@echo "### this file is generated by jrd_build_plf.mk, used as a flag, do not modify it" > $(INDEPENDENT_APP_FLAG)
	@echo building the customized independent app done.
