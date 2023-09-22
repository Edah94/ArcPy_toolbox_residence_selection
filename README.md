# ArcPy Toolbox for Automating the Suitability Analysis Workflow for Residence Selection
This project presents an automated toolbox developed using ArcGIS, designed to simplify the process of selecting the ideal residence location in Salzburg. The toolbox employs a multicriteria spatial analysis method, taking into account various environmental and service factors, including proximity to schools, parks, shopping malls, restaurants, and public transportation. Users can customize their preferences by assigning weights to criteria, allowing for a tailored selection process. While the project prioritizes technical implementation over result accuracy, it serves as a valuable tool for homebuyers and real estate agents in considering both service accessibility and environmental quality when choosing a place to reside. This open-source project showcases the potential of geospatial analysis for real-world decision-making.

## Project motivation

The project's inspiration encompasses two primary aspects. Firstly, it aims to serve as a place for my technical learning and practical experience, particularly in Python scripting within ArcGIS environment, namely ArcPy, as well as broader technical skills development within the field of programming and automation. Secondly, it carries a social motivation, intending to assist individuals who are not expers in Geographic Information Sytems (GIS) by providing them with the tools to perform spatial analysis for their individual requirements. The project focuses on helping individuals find the most suitable residential locations, reducing the need for manual calculations related to environmental proximity in the process.7

## Further considerations

Further projects envision involves epxanding beyond the ESRI's environment, recuding reliance on its functionalities, and transitioning towards open-source technologies. This transition would culminate in the dissemination of the project through a easily reachable and user-friendly website. In terms of analysis, the calculations should be shifted away from determining buffer zones based on environmental factors and instead propose them in relation to road infrastructure. This approach would result in more reliable results concerning the proximity of the factors considered in the claculation as it leverages a foundation for human mobility. Adopting this approach would allow for the inclusion of geographical opstacles like rivers and hills in the calculation process.

## How it works

**Dependency**: 
- ArcGIS Pro V. 2.9 license(the use of other versions might cause incompatibilities with the toolbox)

**Please follow these steps**:
1. Download the ['src'](https://github.com/Edah94/ArcPy_toolbox_residence_selection/raw/main/src) directory and save it to your preferred folder;
2. In ArcGIS Pro, navigate to the directory where you saved the 'src' directory. Inside the directory, you will find the **ResidenceSelectionSalzburg.atbx** toolbox;
3. Open the toolbox and customize the analysis by selecting the factors you want to consider. Assign weights and distances to each factor. Keep in mind that for each factor you include, you'll need to specify a total of five different distance values.
4. Run the analysis, and wait for a moment as the results are generated and displayed on the map view.
   - In case the resulting layer does not render on a map tab automatically, make sure that you have a map tab open within the project. If the issue still persists, you can alternatively naviage to the **output.gbd** geodatabase within the **geodatabase** directory and open the **salzburg_buildings_suitability** layer within the project.
   - If you encounter any issues during the analysis, you can review the 'View Details' for error messages and attempt to resolve the problem before rerunning the analysis.
