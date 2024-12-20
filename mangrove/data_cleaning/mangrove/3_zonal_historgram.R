# generate zonal statistics table for mangrove in 2010 to 2020 and historical mangrove
# for area between shoreline and village and spatial IV version of it 

library(sf)
library(tidyverse)
library(raster)
library(exactextractr)
rm(list=ls())

# for distance to village
filenames <- list.files("C:\\Users\\zhu.2906\\Documents\\ArcGIS\\Projects\\tmf processing\\output",full.names=TRUE)

for (i in list("1600","3200", "4800")){
  # load sd shapefiles in india and clean data
  sd= read_sf(paste0('C:\\Users\\zhu.2906\\Documents\\ArcGIS\\Projects\\shrug_india\\output_polygon_distance\\new_village_shore_lines_',i,'_buffer.shp'))
  sd <- sd['IN_FID']
  
  for (file in filenames){
    if ((substr(file, nchar(file)-3, nchar(file)) == '.tif') &
        (substr(file, nchar(file)-7, nchar(file)-4)>='2010')){
      print(file)
      raster<-raster(file)
      
      
      # zonal histogram
      sd_zonal <- exactextractr::exact_extract(raster, sd,
                                               append_cols=T,
                                               summarize_df=T,
                                               fun=function(x) x %>%
                                                 group_by(code = as.character(value)) %>%
                                                 summarise(area = sum(coverage_fraction)))
      # change to good format
      sd_zonal<-sd_zonal %>%
                      pivot_wider(names_from = 'code', values_from = 'area',
                                  names_glue = "code_{code}" )
      
      write.csv(sd_zonal,paste0("C:\\Users\\zhu.2906\\Documents\\ArcGIS\\Projects\\shrug_india\\output_polygon_distance\\",
                                "new_village_shore_lines_",i,"_",substr(file, nchar(file)-7, nchar(file)-4),".csv"), row.names = FALSE)
    }
  }
}

# for IV
# for distance to village
filenames <- list.files("C:\\Users\\zhu.2906\\Documents\\ArcGIS\\Projects\\tmf processing\\output",full.names=TRUE)

for (i in list("1600","3200", "4800")){
  # load sd shapefiles in india and clean data
  sd= read_sf(paste0('C:\\Users\\zhu.2906\\OneDrive - The Ohio State University\\pythonProject\\India_mangroves_python\\data_cleaning\\shurug_update\\spatial IV\\mangrove_iv_',i,'_buffer.shp'))
  sd <- sd['IN_FID']
  
  for (file in filenames){
    if ((substr(file, nchar(file)-3, nchar(file)) == '.tif') &
        (substr(file, nchar(file)-7, nchar(file)-4)>='2010')){
      print(file)
      raster<-raster(file)
      
      
      # zonal histogram
      sd_zonal <- exactextractr::exact_extract(raster, sd,
                                               append_cols=T,
                                               summarize_df=T,
                                               fun=function(x) x %>%
                                                 group_by(code = as.character(value)) %>%
                                                 summarise(area = sum(coverage_fraction)))
      # change to good format
      sd_zonal<-sd_zonal %>%
        pivot_wider(names_from = 'code', values_from = 'area',
                    names_glue = "code_{code}" )
      
      write.csv(sd_zonal,paste0("C:\\Users\\zhu.2906\\Documents\\ArcGIS\\Projects\\shrug_india\\output_polygon_distance\\",
                                "new_village_shore_lines_IV_",i,"_",substr(file, nchar(file)-7, nchar(file)-4),".csv"), row.names = FALSE)
    }
  }
}

# 1950 mangrove
for (i in list("1600","3200", "4800")){
  sd= read_sf(paste0('C:\\Users\\zhu.2906\\Documents\\ArcGIS\\Projects\\shrug_india\\output_polygon_distance\\new_village_shore_lines_',i,'_buffer.shp'))
  sd <- sd['IN_FID']
  raster<-raster('C:\\Users\\zhu.2906\\Documents\\ArcGIS\\Projects\\shrug_india\\mangrove_1950_raster.tif')
  
  
  # zonal histogram
  sd_zonal <- exactextractr::exact_extract(raster, sd,
                                           append_cols=T,
                                           summarize_df=T,
                                           fun=function(x) x %>%
                                             group_by(code = as.character(value)) %>%
                                             summarise(area = sum(coverage_fraction)))
  # change to good format
  sd_zonal<-sd_zonal %>%
    pivot_wider(names_from = 'code', values_from = 'area',
                names_glue = "code_{code}" )
  
  write.csv(sd_zonal,paste0("C:\\Users\\zhu.2906\\Documents\\ArcGIS\\Projects\\shrug_india\\output_polygon_distance\\",
                            "new_village_shore_lines_1950","_",i,".csv"), row.names = FALSE)
}
