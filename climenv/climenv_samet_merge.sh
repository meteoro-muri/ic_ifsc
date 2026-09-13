#!/bin/bash
#
###########################################################
#                                                         #
# Script para gerar Série temporal dos dados de          #
# previsao do modelo GFS para as localidades do Multilab  # 
#                                                         #
#                                                         #
#    Autor: Murilo e Mario  - PCAM/IFSC  Data: 06/04/2026 #
#           Murilo e Mario  - PCAM/IFSC  Data: 06/04/2026 #
###########################################################
#
export LC_NUMERIC=en_US.UTF-8     ;# Comando para executar operacoes decimais
#
mt=(' ' 'JAN' 'FEB' 'MAR' 'APR' 'MAY' 'JUN' 'JUL' 'AUG' 'SEP' 'OCT' 'NOV' 'DEC')
dt=(' ' '31'  '28'  '31'  '30'  '31'  '30'  '31'  '31'  '30'  '31'  '30'  '31')
#
########################################################
# Definir os caminhos do scrips                        #
########################################################
#
path_scr=$HOME/scripts/climenv_gfs
path_mer=/media/dados/operacao/merge
path_sam=/media/dados/operacao/samet
path_gfs=/media/dados/operacao/gfs/0p50
#
path_tmp=$path_scr/tmp_data
path_out=$path_scr/cat_data
#
mkdir -p $path_scr
mkdir -p $path_out
mkdir -p $path_tmp
rm -rf ${path_tmp}/*.nc
#
#
cd $path_scr
###----------------------------------------------------------------###
### Entra com a Data Inicial                                       ###
###----------------------------------------------------------------###
#
if [ -z $1 ] 
then
 echo     
 echo "Entre com a Data Inicial -> <aammddhh> <ndays>"
 echo "Ex.:  ./climenv_gfs.sh 2026030100 14" 
 echo     
 exit
else
 dati=$1
fi
#
if [ -z $2 ] 
then
 echo     
 echo "Entre com a Data Inicial -> <aammddhh> <ndays>"
 echo "Ex.:  ./climenv_gfs.sh 2026030100 14" 
 echo     
 exit
else
 ndays=$2
fi

#
######################################################################
###		         LENDO A DATA INICIAL          		   ###
######################################################################
#
ai=`echo $dati | awk '{ print substr($1,1,4)}'`
mi=`echo $dati | awk '{ print substr($1,5,2)}'`
moni=${mt[`echo $mi | awk '{ print $1*1}'`]}
di=`echo $dati | awk '{ print substr($1,7,2)}'`
hi=`echo $dati | awk '{ print substr($1,9,2)}'`
#
datafin=`date -u --date="${ai}${mi}${di} + ${ndays} days" +%Y%m%d%H`;# Linux
af=`echo $datafin | awk '{ print substr($1,1,4)}'`
mf=`echo $datafin | awk '{ print substr($1,5,2)}'`
monf=${mt[`echo $mf | awk '{ print $1*1}'`]}
df=`echo $datafin | awk '{ print substr($1,7,2)}'`
hf=`echo $datafin | awk '{ print substr($1,9,2)}'`

cd $path_scr
echo " Data Inicial -> " ${ai}${mi}${di}${hi}
echo " Data Final   -> " ${af}${mf}${df}${hf}
#

#
######################################################################
###	INICIA O TRATAMENTO DOS DADOS DO MERGE E SAMET         		   ###
######################################################################
#
for (( i = 0; i <= $ndays; i++ ))
do
#
    data=`date -u --date="$ai${mi}${di} + $i days" +%Y%m%d%H`;# Linux
    aa=`echo $data | awk '{ print substr($1,1,4)}'`
    mm=`echo $data | awk '{ print substr($1,5,2)}'`
    mon=${mt[`echo $mm | awk '{ print $1*1}'`]}
    dd=`echo $data | awk '{ print substr($1,7,2)}'`
    hh=`echo $data | awk '{ print substr($1,9,2)}'`
    #
    
    echo "Data -> "$data $ano $mmm $diai $diaf
    echo "Path -> "${path_sam}/hourly/${aa}/${mm}/${dd}
    cd ${path_sam}/hourly/${aa}/${mm}/${dd}
    cdo mergetime SAMeT_CPTEC_${aa}${mm}${dd}*.nc ${path_tmp}/SAMeT_CPTEC_${aa}${mm}${dd}.nc
    cd ${path_mer}/hourly/${aa}/${mm}/${dd}
    cdo mergetime MERGE_CPTEC_${aa}${mm}${dd}*.grib2 ${path_tmp}/MERGE_CPTEC_${aa}${mm}${dd}.nc
    #    
    pwd
done

cd ${path_tmp}
cdo mergetime SAMeT_CPTEC_*.nc ${path_tmp}/new_SAMeT_CPTEC_${ai}${mi}${di}.nc
rm -rf SAMeT_CPTEC_????????.nc
cdo selname,tt2m new_SAMeT_CPTEC_${ai}${mi}${di}.nc SAMeT_CPTEC_${ai}${mi}${di}.nc
rm -rf new_SAMeT_CPTEC_${ai}${mi}${di}.nc
echo "Arquivo Gerado -> "SAMeT_CPTEC_${ai}${mi}${di}.nc
#
cd ${path_tmp}
cdo mergetime MERGE_CPTEC_*.nc ${path_tmp}/new_MERGE_CPTEC_${ai}${mi}${di}.nc
rm -rf MERGE_CPTEC_????????.nc
cdo selname,prec new_MERGE_CPTEC_${ai}${mi}${di}.nc MERGE_CPTEC_${ai}${mi}${di}.nc
rm -rf new_MERGE_CPTEC_${ai}${mi}${di}.nc
echo "Arquivo Gerado -> "MERGE_CPTEC_${ai}${mi}${di}.nc

#
######################################################################
###	GERA OS ARQUIVOS TXT DAS �LOCLAIDADES SELECIONADAS         ###
######################################################################
for (( loc = 1; loc <= 4; loc++ ))
do  
 if  [ $loc -eq 1 ]; then lat=-23.3 ; lon=-48.5 ; cit=florianopolis ; fi
 if  [ $loc -eq 2 ]; then lat=-27.1 ; lon=-52.5 ; cit=chapeco ; fi
 if  [ $loc -eq 3 ]; then lat=-28.6 ; lon=-49.3 ; cit=criciuma ; fi
 if  [ $loc -eq 4 ]; then lat=-26.3 ; lon=-48.9 ; cit=joinville ; fi

 #
 # Gerando TXT do SAMET
 #
 cdo -outputtab,date,time,lon,lat,value -remapnn,"lon=${lon}_lat=${lat}" ${path_tmp}/SAMeT_CPTEC_${ai}${mi}${di}.nc > $path_out/samet_tmp2m_hor_${cit}_${ai}${mi}${di}${hi}_${ndays}.txt
 echo "Arquivo Gerado Horario tmp2m p/ ",${ndays}," dias SAMET -> "$path_out/samet_tmp2m_hor_${cit}_${ai}${mi}${di}${hi}_${ndays}.txt
 #
 cdo -outputtab,date,time,lon,lat,value -remapnn,"lon=${lon}_lat=${lat}" ${path_tmp}/MERGE_CPTEC_${ai}${mi}${di}.nc > $path_out/merge_prec_hor_${cit}_${ai}${mi}${di}${hi}_${ndays}.txt
 echo "Arquivo Gerado Horario tmp2m p/ ",${ndays}," dias MERGE -> "$path_out/merge_prec_hor_${cit}_${ai}${mi}${di}${hi}_${ndays}.txt

done

#
######################################################################
###	DELETA OS ARQUIVOS TEMPORTÁRIOS                           ###
######################################################################
#
rm -rf ${path_tmp}/*.nc
 
exit


