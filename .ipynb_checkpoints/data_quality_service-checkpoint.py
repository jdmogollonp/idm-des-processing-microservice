import os
import pandas as pd
import great_expectations as ge
import great_expectations.jupyter_ux
from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.profile.user_configurable_profiler import UserConfigurableProfiler
from great_expectations.data_context.types.resource_identifiers import ExpectationSuiteIdentifier
from great_expectations.exceptions import DataContextError
from storage_service import S3Client

import warnings
warnings.filterwarnings("ignore")

pd.set_option('display.float_format', lambda x: '%.0f' % x)

s3_client = S3Client()



class Expectations:
    def __init__(self,filename,bucket):
        df = ge.read_csv(f'data/{filename}')
        df = df[['PatientNumber', 'date', 'stage', 'activity']]
        df.reset_index(drop = True, inplace = True)
        self.df = df
        self.local_path = 'great_expectations/uncommitted/data_docs/local_site/expectations/'
        self.s3_bucket = bucket
        self.context = ge.data_context.DataContext()
        self.expectation_suite_name = 'my_data_expectations'
        self.suite = self.context.create_expectation_suite(expectation_suite_name=self.expectation_suite_name, overwrite_existing=True)
        
        
    def get_context(self):    
        self.context.save_expectation_suite(expectation_suite=self.suite, expectation_suite_name=self.expectation_suite_name)
        self.suite_identifier = ExpectationSuiteIdentifier(expectation_suite_name=self.expectation_suite_name)
        self.context.build_data_docs(resource_identifiers=[self.suite_identifier])
        self.context.open_data_docs(resource_identifier=self.suite_identifier)

    def get_expectations(self):
        df_ge = ge.from_pandas(self.df)
        batch_kwargs = {
            "datasource": 'my_data_files_dir',
            "dataset": df_ge,
        }
        batch = self.context.get_batch(
            batch_kwargs=batch_kwargs,
            expectation_suite_name="my_data_expectations")
        profiler = UserConfigurableProfiler(profile_dataset=batch)
        suite = profiler.build_suite()
        
        # We need to re-create our batch to link the batch with our new suite
        batch = self.context.get_batch(
        batch_kwargs=batch_kwargs,
        expectation_suite_name=self.expectation_suite_name)

        # Running validation
        results = self.context.run_validation_operator("action_list_operator", assets_to_validate=[batch])
        validation_result_identifier = results.list_validation_result_identifiers()[0]
        
        # Saving our expectation suite
        self.context.save_expectation_suite(self.suite, self.expectation_suite_name)

        # Building and opening Data Docs
        self.context.build_data_docs()
        self.context.open_data_docs(validation_result_identifier)
        
    def upload_to_s3(self):
        s3_client.upload_file(self.local_path+'my_data_expectations.html', self.s3_bucket)
        
    def clear_results_folder(self):
        os.remove(self.local_path+'my_data_expectations.html')
        
    def run(self):
        self.define_expectations()
        self.get_context()
        self.get_expectations()
        self.upload_to_s3()
        self.clear_results_folder()
        return True
        
    
    def define_expectations(self):
        
        # Verify column names
        expectation_column_names = ExpectationConfiguration(
            expectation_type="expect_table_columns_to_match_set",
            
            kwargs={
                "column_set": ["PatientNumber","date","stage","activity","TriagePriority"],
                'exact_match': True
            },

            meta={
                "notes": {
                    "format": "markdown",
                    "content": "Column names are case sentisitive"
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_column_names, overwrite_existing=True)

        # Verify data types
        expectation_data_type_patient_number = ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={
                "column": "PatientNumber",
                "type_": 'int',
            },
            meta={
                "notes": {
                    "format": "markdown",
                    "content": "PatientNumber should be an integer value"
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_data_type_patient_number, overwrite_existing=True)


        expectation_data_type_activity = ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={
                "column": "activity" ,
                "type_": "str" 
            },
            meta={
                "notes": {
                    "format": "markdown",
                    "content": "activity should be a string value"
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_data_type_activity, overwrite_existing=True)

        expectation_data_type_event = ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={
                "column": "stage" ,
                "type_": "str" 
            },
            meta={
                "notes": {
                    "format": "markdown",
                    "content": "stage should be a string value"
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_data_type_event, overwrite_existing=True)

        expectation_data_type_date = ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={
                "column": "date",
                "type_": "string"
            },
            meta={
                "notes": {
                    "format": "markdown",
                    "content": "data should be a  string in yyyy-MM-dd HH:mm:ss format "
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_data_type_date, overwrite_existing=True)

        expectation_data_type_triage_priority = ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_of_type",
            kwargs={
                "column": "TriagePriority",
                "type_": "str"
            },
            meta={
                "notes": {
                    "format": "markdown",
                    "content": "TriagePriority should be a string value"
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_data_type_triage_priority, overwrite_existing=True)

        # Identify missing values  

        expectation_missing_values_patient_number = ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={
                "column": "PatientNumber",
                "mostly": 1
            },
            meta={
                "notes": {
                    "format": "markdown",
                    "content": "This data column cannot contain missing values."
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_missing_values_patient_number, overwrite_existing=True)

        expectation_missing_values_stage = ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={
                "column": "stage",
                "mostly": 1
            },
            meta={
                "notes": {
                    "format": "markdown",
                    "content": "This data column cannot contain missing values."
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_missing_values_stage, overwrite_existing=True)

        expectation_missing_values_date = ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={
                "column": "date",
                "mostly": 1
            },
            meta={
                "notes": {
                    "format": "markdown",
                    "content": "This data column cannot contain missing values."
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_missing_values_date, overwrite_existing=True)

        expectation_missing_values_activity = ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={
                "column": "activity",
                "mostly": 1
            },
            meta={
                "notes": {
                    "format": "markdown",
                    "content": "This data column cannot contain missing values."
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_missing_values_activity, overwrite_existing=True)

        expectation_missing_values_triage_priority = ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={
                "column": "TriagePriority",
                "mostly": 1
            },
            meta={
                "notes": {
                    "format": "markdown",
                    "content": "This data column cannot contain missing values."
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_missing_values_triage_priority, overwrite_existing=True)

       
        expectation_missing_values_triage_priority = ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={
                "column": "TriagePriority",
                "mostly": 1
            },
            meta={
                "notes": {
                    "format": "markdown",
                    "content": "This data column cannot contain missing values."
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_missing_values_triage_priority, overwrite_existing=True)


        # Check Expected Value  #PatientNumber	date	stage	activity TriagePriority

        expectation_expected_values_severity_index = ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_in_set",
            kwargs={
                "column": "TriagePriority",
                "value_set": ["Orange","Vert","Rouge"],
                "mostly" : 1
            },
            meta={
                "notes": {
                    "format": "markdown",
                    "content": "Expected severity index values are:Orange,Vert,Rouge"
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_expected_values_severity_index, overwrite_existing=True)


        expectation_expected_values_Event = ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_in_set",
            kwargs={
                "column": "activity",
                "value_set": ["TriageStartDateTime",
                                "TriageEndDateTime",
                                "biochimieBAStartDateTime",
                                "biochimieTakeBADateTime",
                                "biochimieResultBADateTime",
                                "hematologieBAStartDateTime",
                                "hematologieTakeBADateTime",
                                "hematologieResultBADateTime",
                                "coagulationBAStartDateTime",
                                "coagulationTakeBADateTime",
                                "coagulationResultBADateTime",
                                "RXPrescriptionDateTime",
                                "RXRealizationDateTime",
                                "RMIRealizationDateTime",
                                "RMIResultBADateTime",
                                "biochimeBAStartDateTime",
                                "biochimeTakeBADateTime",
                                "biochimeResultBADateTime"],
                "mostly" : 1
            },
            meta={
                "notes": {
                    "format": "markdown",
                    "content": """ Expected event values are TriageStartDateTime, TriageEndDateTime,biochimieBAStartDateTime,biochimieTakeBADateTime,
                    biochimieResultBADateTime, hematologieBAStartDateTime,  hematologieTakeBADateTime,
                                                                    hematologieResultBADateTime,  coagulationBAStartDateTime,coagulationTakeBADateTime,
                                                                    coagulationResultBADateTime, RXPrescriptionDateTime,RXRealizationDateTime,
                                                                    RMIRealizationDateTime,RMIResultBADateTime,biochimeBAStartDateTime,
                                                                    biochimeTakeBADateTime, biochimeResultBADateTime """
                                                                   
                }
            },
        )
        self.suite.add_expectation(expectation_configuration=expectation_expected_values_Event, overwrite_existing=True)
    