from mongoengine import BooleanField, DateTimeField, Document, DynamicEmbeddedDocument, EmbeddedDocument, EmbeddedDocumentField, StringField, ListField
from server.models.base_components import ExactValue
from datetime import datetime, date, time, timezone, timedelta

class CheckSpec(EmbeddedDocument):
    """
    Represents the specification check for a measured result.

    Attributes:
        Status (str): Indicates the status of the check.
        CheckAt (datetime): The timestamp when the check was performed.
    """
    Status = StringField(default="UNCHECKED", choices=['PASS', 'FAIL', 'UNCHECKED', 'NOT_SPECIFIED'])
    CheckAt = DateTimeField(default=lambda: datetime.now(datetime.timezone.utc))


class MeasuredResultEntry(DynamicEmbeddedDocument):
    """
    Attributes:
        DataType (str): The type of data being measured (e.g., "Voltage", "Current").
        ExactValue (ExactValue): The exact measured value and its unit.
        CheckSpec (CheckSpec): The specification check result and timestamp.
    """
    DataType = StringField(required=True)
    ExactValue = EmbeddedDocumentField(ExactValue)
    CheckSpec = EmbeddedDocumentField(CheckSpec)


class SubTestData(EmbeddedDocument):
    """
    Represents a single parameter or measured result for a sub-test.

    Attributes:
        DataName (str): The name or label of the parameter/result (e.g., "Voltage", "Current").
        ExactValue (ExactValue): The measured or specified value of the parameter/result.
        TextValue (str): A descriptive or abstract representation of the value.

    """
    DataName = StringField(required=True)
    ExactValue = EmbeddedDocumentField(ExactValue)
    TextValue = StringField()


class SubTest(EmbeddedDocument):
    """
    Represents a single sub-test conducted as part of the inspection.

    Attributes:
        TestType (str): The type of sub-test (e.g., "RemoteControlTest", "StartupTest").
        Parameters (list): A list of input parameters used for the sub-test.
        MeasuredResults (list): A list of measured results or output data from the sub-test.
        IsPassed (bool): Indicates whether the sub-test passed or failed.
    """
    TestType =  StringField(required=True)
    Parameters = ListField(EmbeddedDocumentField(SubTestData))
    MeasuredResults = ListField(EmbeddedDocumentField(SubTestData))
    IsPassed = BooleanField()


class InspectionAttachmentDetails(DynamicEmbeddedDocument):
    """_
    """
    MeasuredTarget = StringField()
    OutputCurrent = StringField(choices=['NoLoad', 'MinimumLoad', 'MaximumLoad'])
    InputVoltage = StringField(choices=['LowLine', 'NominalLine', 'HighLine'])


class InspectionAttachment(EmbeddedDocument):
    """
    Represents an attachment in the inspection record, supporting multiple types with optional details.

    Attributes:
        AttachmentType (str): The type of the attachment (e.g., OscilloscopeImage, ATEExecutionLog, AnalysisReport, Others).
        FilePath (str): The file path where the attachment is stored.
        Description (str): A brief description of the attachment.
        Details (InspectionAttachmentDetails): Optional specific details for the attachment.
    """
    AttachmentType = StringField(choices=['OscilloscopeImage', 'ATEExecutionLog', 'AnalysisReport', 'Others'], required=True)
    FilePath = StringField(required=True)
    Description = StringField()
    Details = EmbeddedDocumentField(InspectionAttachmentDetails)


class InspectionRecord(Document):
    """
    Represents an inspection record for a specific model in the manufacturing process.

    Attributes:
        ModelNumber (str): The unique identifier for the product model being inspected.
        ManufacturingOrderNumber (str): The manufactu0ring order associated with this inspection.
        InspectionStage (str): The stage of inspection, either "SemiProduct" or "FinalProduct".
        TestMethod (str): The method of testing (e.g., "Manual", "Automated", "Hybrid").
        EquipmentIds (list): A list of IDs of the equipment used during the inspection process.
        InspectorIds (list): A list of IDs of the inspectors who performed this inspection.
        FinishAt (datetime): The timestamp when the inspection was completed.
        AmbientTemperature (ExactValue): The ambient temperature during the inspection.
        RelativeHumidity (ExactValue): The relative humidity during the inspection.
        AtmosphericPressure (ExactValue): The atmospheric pressure during the inspection.
        SubTests (list): A list of sub-tests conducted as part of this inspection.
        MeasuredResultTable (list): A list of measured results from the inspection.
        Attachments (list):
        Notes (str): Additional notes or comments about the inspection.
    """
    ModelNumber = StringField(required=True)
    ManufacturingOrderNumber = StringField()
    InspectionStage = StringField(choices=["SemiProduct", "FinalProduct"])
    TestMethod = StringField(required=True, choices=["Manual", "Automated", "Hybrid", "Simulation"])
    EquipmentIds = ListField(StringField())
    InspectorIds = ListField(StringField())
    FinishAt = DateTimeField(required=True, default=lambda: datetime.now(datetime.timezone.utc))
    AmbientTemperature = EmbeddedDocumentField(ExactValue)
    RelativeHumidity = EmbeddedDocumentField(ExactValue)
    AtmosphericPressure = EmbeddedDocumentField(ExactValue)
    SubTests = ListField(EmbeddedDocumentField(SubTest))
    MeasuredResultTable = ListField(EmbeddedDocumentField(MeasuredResultEntry))
    Attachments = ListField(EmbeddedDocumentField(InspectionAttachment))
    Notes = StringField()

    meta = {
        'collection': 'InspectionRecord',
        'ordering': ['-FinishAt'],
    }

    @staticmethod
    def date_to_datetime(date_input: str | date, format: str = "%Y-%m-%d") -> datetime:
        """
        Converts a date or date string to a datetime object with a default time of 17:20 (GMT+8).

        Args:
            date_input (str | date): The input date, either as a string in the specified format or a date object.
            format (str): The format of the input date string (default is "YYYY-MM-DD").

        Returns:
            datetime: A datetime object with the default time set to 17:20 (GMT+8).

        Raises:
            ValueError: If the input string cannot be parsed into a valid date.
        """
        # Default time to set (17:20)
        default_time = time(17, 20)

        # Parse input if it's a string
        if isinstance(date_input, str):
            try:
                parsed_date = datetime.strptime(date_input, format).date()
            except ValueError:
                raise ValueError(f"Invalid date string format: {date_input}. Expected format: {format}.")
        elif isinstance(date_input, date):
            parsed_date = date_input
        else:
            raise TypeError("Input must be a date object or a string in the specified format.")

        # Combine date and default time
        combined_datetime = datetime.combine(parsed_date, default_time)

        # Set timezone to GMT+8
        gmt_plus_8 = timezone(timedelta(hours=8))
        return combined_datetime.replace(tzinfo=gmt_plus_8)
