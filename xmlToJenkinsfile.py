import xml.etree.ElementTree as ET

def parse_xml_to_jenkinsfile(xml_file, output_file):
    """
    Parse a Jenkins job configuration XML file and generate a declarative Jenkinsfile.

    The resulting Jenkinsfile will include:
    - A 'Checkout' stage if an SCM configuration is found.
    - One stage per shell command found in the builders section.
    This approach aims to be universal and compliant with standard Jenkins Declarative Pipeline syntax.
    """

    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Initialize Jenkinsfile structure
    jenkinsfile = []
    jenkinsfile.append("pipeline {")
    jenkinsfile.append("    agent any")
    jenkinsfile.append("    stages {")

    # Handle SCM stage if available
    scm = root.find("scm")
    if scm is not None:
        git_url = scm.find(".//url").text if scm.find(".//url") is not None else "https://example.com/repo.git"
        branch = scm.find(".//name").text if scm.find(".//name") is not None else "main"

        jenkinsfile.append("        stage('Checkout') {")
        jenkinsfile.append("            steps {")
        jenkinsfile.append(f"                git branch: '{branch}', url: '{git_url}'")
        jenkinsfile.append("            }")
        jenkinsfile.append("        }")

    # Handle builders (shell commands)
    builders = root.find("builders")
    if builders is not None:
        shell_tasks = builders.findall("hudson.tasks.Shell")
        for idx, shell in enumerate(shell_tasks, start=1):
            command_element = shell.find("command")
            if command_element is not None and command_element.text:
                command = command_element.text.strip()
                stage_name = f"Build Step {idx}"
                jenkinsfile.append(f"        stage('{stage_name}') {{")
                jenkinsfile.append("            steps {")
                jenkinsfile.append(f"                sh '''{command}'''")
                jenkinsfile.append("            }")
                jenkinsfile.append("        }")

    # Close Jenkinsfile structure
    jenkinsfile.append("    }")
    jenkinsfile.append("}")

    # Write the Jenkinsfile
    with open(output_file, "w") as f:
        f.write("\n".join(jenkinsfile))

    print(f"Jenkinsfile generated successfully: {output_file}")


# Example usage:
# xml_path = "config.xml"
# jenkinsfile_path = "Jenkinsfile"
# parse_xml_to_jenkinsfile(xml_path, jenkinsfile_path)
