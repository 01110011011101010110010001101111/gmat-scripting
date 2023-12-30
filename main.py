"""
Generates a script for GMAT to run
"""

class GMATScript:
    def __init__(self):
        """
        Creates new GMAT Script Object
        """
        self.final_script = ""
        self.formations = {}

    def create_formation(self, satellite_names, elements, formation_name="form"):
        """
        Adds Satellites to Script and Creates Formation
        """
        # add satellites to the formation dictionary
        if type(satellite_names) != list:
            raise Exception("satellites_names must be a list")

        # adds the formation to the dictionary and precompute useful strings
        self.formations[formation_name] = {
            "satellite_names": satellite_names,
            "satellite_set": f"{{ {', '.join(satellite_names)} }}",
        }

        for sat_name, sat_elements in zip(satellite_names, elements):
            ecc = sat_elements["ecc"]
            inc = sat_elements["inc"]
            sma = sat_elements["sma"]
            ta = sat_elements["ta"]
            aop = sat_elements["aop"]
            raan = sat_elements["raan"]

            create_sat = f"""

%----------------------------------------
%---------- Create Spacecraft {sat_name}
%----------------------------------------

Create Spacecraft {sat_name};
GMAT {sat_name}.DateFormat = UTCGregorian;
GMAT {sat_name}.Epoch = '01 Jan 2000 11:59:28.000';
GMAT {sat_name}.CoordinateSystem = EarthMJ2000Eq;
GMAT {sat_name}.DisplayStateType = Keplerian;
GMAT {sat_name}.SMA = {sma};
GMAT {sat_name}.ECC = {ecc};
GMAT {sat_name}.INC = {inc};
GMAT {sat_name}.RAAN = {raan};
GMAT {sat_name}.AOP = {aop};
GMAT {sat_name}.TA = {ta};
GMAT {sat_name}.DryMass = 850;
GMAT {sat_name}.Cd = 2.2;
GMAT {sat_name}.Cr = 1.8;
GMAT {sat_name}.DragArea = 15;
GMAT {sat_name}.SRPArea = 1;
GMAT {sat_name}.SPADDragScaleFactor = 1;
GMAT {sat_name}.SPADSRPScaleFactor = 1;
GMAT {sat_name}.AtmosDensityScaleFactor = 1;
GMAT {sat_name}.ExtendedMassPropertiesModel = 'None';
GMAT {sat_name}.NAIFId = -123456789;
GMAT {sat_name}.NAIFIdReferenceFrame = -123456789;
GMAT {sat_name}.OrbitColor = Red;
GMAT {sat_name}.TargetColor = Teal;
GMAT {sat_name}.OrbitErrorCovariance = [ 1e+70 0 0 0 0 0 ; 0 1e+70 0 0 0 0 ; 0 0 1e+70 0 0 0 ; 0 0 0 1e+70 0 0 ; 0 0 0 0 1e+70 0 ; 0 0 0 0 0 1e+70 ];
GMAT {sat_name}.CdSigma = 1e+70;
GMAT {sat_name}.CrSigma = 1e+70;
GMAT {sat_name}.Id = 'SatId';
GMAT {sat_name}.Attitude = CoordinateSystemFixed;
GMAT {sat_name}.SPADSRPInterpolationMethod = Bilinear;
GMAT {sat_name}.SPADSRPScaleFactorSigma = 1e+70;
GMAT {sat_name}.SPADDragInterpolationMethod = Bilinear;
GMAT {sat_name}.SPADDragScaleFactorSigma = 1e+70;
GMAT {sat_name}.AtmosDensityScaleFactorSigma = 1e+70;
GMAT {sat_name}.ModelFile = '../data/vehicle/models/aura.3ds';
GMAT {sat_name}.ModelOffsetX = 0;
GMAT {sat_name}.ModelOffsetY = 0;
GMAT {sat_name}.ModelOffsetZ = 0;
GMAT {sat_name}.ModelRotationX = 0;
GMAT {sat_name}.ModelRotationY = 0;
GMAT {sat_name}.ModelRotationZ = 0;
GMAT {sat_name}.ModelScale = 1.2;
GMAT {sat_name}.AttitudeDisplayStateType = 'Quaternion';
GMAT {sat_name}.AttitudeRateDisplayStateType = 'AngularVelocity';
GMAT {sat_name}.AttitudeCoordinateSystem = EarthMJ2000Eq;
GMAT {sat_name}.EulerAngleSequence = '321';

"""

            self.final_script = self.final_script + create_sat

        form = f"""

%----------------------------------------
%---------- Formation
%----------------------------------------

Create Formation {formation_name};
GMAT form.Add = {self.formations[formation_name]["satellite_set"]};

"""

        self.final_script = self.final_script + form

        return self.final_script

    def default_add_forcemodel_and_propagator(self):
        default_fm_prop = """

%----------------------------------------
%---------- ForceModels
%----------------------------------------

Create ForceModel fm;
GMAT fm.CentralBody = Earth;
GMAT fm.PointMasses = {Earth, Sun, Luna};
GMAT fm.Drag = None;
GMAT fm.SRP = Off;
GMAT fm.RelativisticCorrection = Off;
GMAT fm.ErrorControl = RSSStep;

%----------------------------------------
%---------- Propagators
%----------------------------------------

Create Propagator prop;
GMAT prop.FM = fm;
GMAT prop.Type = RungeKutta89;
GMAT prop.InitialStepSize = 60;
GMAT prop.Accuracy = 9.999999999999999e-12;
GMAT prop.MinStep = 0.001;
GMAT prop.MaxStep = 2700;
GMAT prop.MaxStepAttempts = 50;
GMAT prop.StopIfAccuracyIsViolated = true;

"""

        self.final_script = self.final_script + default_fm_prop

        return default_fm_prop

    def add_report_file(self, traits, path="SWIPE_ReportFile.tsv"):
        """
        Generates a report file given list of variables
        """
        view = f"""

%----------------------------------------
%---------- Report File
%----------------------------------------

Create ReportFile ReportFile1;
GMAT ReportFile1.SolverIterations = Current;
GMAT ReportFile1.UpperLeft = [ 0 0 ];
GMAT ReportFile1.Size = [ 0 0 ];
GMAT ReportFile1.RelativeZOrder = 0;
GMAT ReportFile1.Maximized = false;
GMAT ReportFile1.Filename = '{path}';
GMAT ReportFile1.Precision = 16;
GMAT ReportFile1.Add = {{ {', '.join(traits)} }};
GMAT ReportFile1.WriteHeaders = true;
GMAT ReportFile1.LeftJustify = On;
GMAT ReportFile1.ZeroFill = Off;
GMAT ReportFile1.FixedWidth = false;
GMAT ReportFile1.Delimiter = '  ';
GMAT ReportFile1.ColumnWidth = 23;
GMAT ReportFile1.WriteReport = true;

"""

        self.final_script = self.final_script + view

        return view

    def default_mission_sequence(self, sat, time_amount = 1.0, time_unit = "ElapsedDays"):
        """
        Runs the default mission sequence for formations
        """

        mission_seq = f"""

%----------------------------------------
%---------- Mission Sequence
%----------------------------------------


BeginMissionSequence;

Propagate 'Prop {time_amount} {time_unit}' prop(form) {{ {sat}.{time_unit} = {time_amount} }};

"""

        self.final_script = self.final_script + mission_seq

        return mission_seq

    def save_file(self, filename="Test_Vector"):
        text_file = open(filename, "w")
        text_file.write(self.final_script)
        text_file.close()
