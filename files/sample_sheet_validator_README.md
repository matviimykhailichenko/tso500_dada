Sample Sheet Validator for TSO500
=================================

Instructions
------------
1. Drop the sample sheet here
2. Wait for a minute
3. Sample sheet has been validated!


General Rules
-------------
- Every section must match exactly the expected headers and contents defined in the template.  
- Any extra or missing section headers → BAD_HEADER is added to the name of the sample sheet file.  
  Example: SampleSheet.csv → SampleSheet_BAD_HEADER.csv  
- Any extra or missing lines within a section → BAD_<SECTIONNAME> is added to the name of the sample sheet file.  
  Example: SampleSheet_Analysis.csv → SampleSheet_Analysis_BAD_<SECTIONNAME>.csv  

Exceptions:
- RunName (can be omitted/changed in [Header])  
- Sample_ID (can vary, but must follow naming rules)


Naming
------
- NSX+ → SampleSheet_Analysis.csv  
  (because there is another sample sheet named SampleSheet.csv for demultiplexing on the on-board DRAGEN)  

- NSQ6000 → SampleSheet.csv  


TSO500L_Data Section
--------------------
- Index columns (Index, Index2) must be valid index pairs from Set A or Set B.


Sample_ID Rules
---------------
Allowed characters:
- Uppercase and lowercase letters (A–Z, a–z)  
- Digits (0–9)  
- Underscore (_)  
- Hyphen (-)  

Anything outside this → ❌ BAD_SAMPLE_ID
