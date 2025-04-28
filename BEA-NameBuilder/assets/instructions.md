# BEA NameBuilder User Instructions

## Overview
BEA NameBuilder is a web application designed to create and generate standardized file names based on user-defined naming conventions. 
It allows users to build a naming convention with metadata (Date, Categorical, Numerical), specify separators, and generate file names with QR codes for easy sharing.  
We have used Harvard's plan and design file-naming-conventions as a guide for the app.
* https://datamanagement.hms.harvard.edu/plan-design/file-naming-conventions

## Getting Started
1. **Access the Application**: Open the BEA NameBuilder in a web browser. `http://localhost:8501/`
2. **Prerequisites**: Ensure you have a modern web browser and access to the application files, including the `assets` folder with `template.json` and `options.json`.
3. **Navigation**: The app has two main sections:
   - **Home**: Displays these instructions for guidance.
   - **NameBuilder**: Contains tools to build a naming convention and generate file names.

## Using the Application
### Sidebar navigation
### 1. Home Page
- **Purpose**: Provides an overview and instructions (this document).
- **Action**: Read the instructions to understand how to use the app.

### 2. Build Convention (🔨 Build Convention!)
This section allows you to create a custom naming convention.

#### Steps:
1. **Name Your Convention**:
   - Enter a unique name for your convention (e.g., "Thesis_2025").
   - Default: Uses the current date (e.g., `20250428_naming_convention`).
   - Preview the convention name as you type.

2. **Choose Metadata Types**:
   - Select at least one metadata type: **Date**, **Categorical**, or **Numerical**.
   - **Date**: For date-based metadata (e.g., production date).
   - **Categorical**: For predefined categories (e.g., initials like "BEA").
   - **Numerical**: For numeric values (e.g., a numerator or temperature).
   - Use the table editor to add metadata entries:
     - **Date**: Specify a description and date format (e.g., YYYYMMDD).
     - **Categorical**: Add category names (subcategories added later).
     - **Numerical**: Define description, lower/upper limits, and digit count.

3. **Set Metadata Order**:
   - Choose the order of metadata in the file name using the multiselect widget.
   - Select at least two metadata types for a valid convention.

4. **Choose Separators**:
   - Select up to two separators: **None (Joined)**, **Underscore <_>**, or **Dash <->**.
   - Assign separators between consecutive metadata pairs in the data editor.
   - Example: For metadata `[Name, Numerator, Date]`, assign separators like `Name_Numerator` and `Numerator-Date`.

5. **Preview Example Name**:
   - View a sample file name based on your convention (e.g., `BEA_0001_YYYYMMDD`).
   - Placeholders are used: `XXX` for categorical, `####` for numerical, and format for date.

6. **Populate Categorical Data**:
   - For categorical metadata, select a category and add key-description pairs.
   - **Key**: 1–3 characters (A-Z, 0-9, uppercase).
   - **Description**: A brief explanation (e.g., "BEA" - "Brian Espinosa").
   - Save changes to update the convention.

7. **Export Convention**:
   - Download the naming convention as a JSON file (e.g., `Thesis_2025.json`).
   - Use this file in the Name Generator or share it with others.

### 3. Name Generator (✒️ Name Generator!)
This section generates file names based on a naming convention.

#### Steps:
1. **Upload Convention**:
   - Upload a JSON file containing your naming convention (e.g., from the Build Convention step).
   - The app validates the file for required keys (`ConventionName`, `MetadataOrder`, `MetadataKeys`, `Separators`).

2. **Enter Metadata Values**:
   - Input values for each metadata type in the convention:
     - **Date**: Select a date using the date picker.
     - **Categorical**: Choose from predefined keys (e.g., "BEA").
     - **Numerical**: Enter a number within the defined limits, formatted to the specified digits.
   - All fields must be filled to generate a file name.

3. **View Generated File Name**:
   - The app displays the generated file name (e.g., `BEA_0001_20250428`).
   - Copy the file name for use in your project.

4. **QR Code**:
   - A QR code is generated for the file name.
   - Scan it with a mobile device to retrieve the file name.
   - Download the QR code as a PNG file (e.g., `BEA_0001_20250428_qr.png`).

## Tips and Best Practices
- **Convention Naming**: Use descriptive names to easily identify the purpose of the convention.
- **Metadata Selection**: Choose metadata relevant to your project (e.g., initials, experiment number, date).
- **Categorical Keys**: Keep keys short and unique (1–3 characters) for concise file names.
- **Numerical Limits**: Set realistic lower and upper limits to avoid invalid inputs.
- **Separators**: Use underscores or dashes for readability; avoid "None (Joined)" for complex metadata.
- **Saving Conventions**: Store exported JSON files securely for reuse or sharing.
- **Resetting**: Refresh the page to start over with a new convention.

## Troubleshooting
- **"File not found" Error**: Ensure `template.json`, `options.json`, and `instructions.md` are in the `assets` folder.
- **"Invalid JSON format" Error**: Check the uploaded JSON file for correct syntax.
- **"Duplicate keys" Error**: Ensure categorical keys are unique and follow the format (1–3 uppercase A-Z, 0-9).
- **Empty Tables**: Fill or remove empty rows in metadata tables before proceeding.
- **Missing Metadata**: Select at least two metadata types and define their order.
- **Encoding Errors**: Ensure `instructions.md` is saved with UTF-8 encoding (use a text editor like VS Code or Notepad++).

## Example
**Convention JSON**:
```json
{
  "ConventionName": "Thesis_2025",
  "ConventionDate": "20250428",
  "MetadataOrder": ["Name/Initials", "Numerator", "Production"],
  "MetadataKeys": {
    "Name/Initials": {
      "Type": "Categorical",
      "Categories": {
        "Key": {"0": "BEA"},
        "Description": {"0": "Brian Espinosa"}
      }
    },
    "Numerator": {
      "Type": "Numerical",
      "Lower": 0,
      "Upper": 9999,
      "Digits": 4
    },
    "Production": {
      "Type": "DateType",
      "Format": "YYYYMMDD"
    }
  },
  "Separators": ["Underscore <_>", "Underscore <_>"]
}
```

**Generated File Name**:
- Inputs: `Name/Initials: BEA`, `Numerator: 1`, `Production: 2025-04-28`
- Output: `BEA_0001_20250428`

**QR Code**: A scannable code containing `BEA_0001_20250428`.

## Support
For issues or questions, contact the application administrator or refer to the documentation in the `assets` folder.

---
*Generated by BEA, April 28, 2025*