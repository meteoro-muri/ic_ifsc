#!/bin/bash
#
###########################################################
#                                                         #
# Script para gerar Serie temporal dos dados de          #
# previsao do modelo WRF para as localidades do Multilab  # 
#                                                         		  #
#                                                        		  #
#    Autor: Daniel, Murilo e Mario  - PCAM/IFSC  Data: 06/04/2026 #
#           Daniel, Murilo e Mario  - PCAM/IFSC  Data: 06/04/2026 #
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
path_cmp=/media/produtos/compara_gfs
path_wrf=/media/dados/operacao/wrf
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
 echo "Ex.:  ./climenv_wrf.sh 2026030100 14" 
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
 echo "Ex.:  ./climenv_wrf.sh 2026030100 14" 
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


for (( i = 0; i <= $ndays; i++ ))
do

	##itera dia a dia pra pegar todas as previsões de todos os dias##
	data_aux=`date -u --date="${ai}${mi}${di} + $i days" +%Y%m%d%H`;# Linux
	echo ${data_aux}
	a_aux=`echo $data_aux | awk '{ print substr($1,1,4)}'`
	m_aux=`echo $data_aux | awk '{ print substr($1,5,2)}'`
	mon_aux=${mt[`echo $mf_aux | awk '{ print $1*1}'`]}
	d_aux=`echo $data_aux | awk '{ print substr($1,7,2)}'`
	h_aux=`echo $data_aux | awk '{ print substr($1,9,2)}'`
	
	
	arq_3d_wrf=${path_wrf}/${a_aux}${m_aux}/wrf_3km_${a_aux}${m_aux}${d_aux}${h_aux}.nc
	echo ${arq_3d_wrf}
	

	#exit
	#
	######################################################################
	## SELECIONA AS VARIAVEIS tmp2M e prec e calcula as estatisticas   ###
	######################################################################
	# TMP2M 3 DIAS
	cdo selname,T2 ${arq_3d_wrf} ${path_tmp}/a1.nc
	cdo subc,273.15  ${path_tmp}/a1.nc ${path_tmp}/a2.nc
	cdo daymean ${path_tmp}/a2.nc ${path_tmp}/a3.nc
	
	# PREC 3 DIAS
	cdo selname,PRECIP ${arq_3d_wrf} ${path_tmp}/c1.nc
	cdo mulc,3600  ${path_tmp}/c1.nc ${path_tmp}/c2.nc
	cdo daysum ${path_tmp}/c2.nc ${path_tmp}/c3.nc
	#exit
	#
	######################################################################
	###	GERA OS ARQUIVOS TXT DAS ÃLOCLAIDADES SELECIONADAS         ###
	######################################################################
	for (( loc = 1; loc <= 4; loc++ ))
	do  
	 if  [ $loc -eq 1 ]; then lat=-27.5 ; lon=-48.5 ; cit=florianopolis ; fi
	 if  [ $loc -eq 2 ]; then lat=-27.1 ; lon=-52.6 ; cit=chapeco ; fi
	 if  [ $loc -eq 3 ]; then lat=-28.6 ; lon=-49.3 ; cit=criciuma ; fi
	 if  [ $loc -eq 4 ]; then lat=-26.3 ; lon=-48.9 ; cit=joinville ; fi
	 #
	 # Gerando Para 03 Dias
	 #
	 echo "sfkdajfsjdafsdasfdadlçkasdf"
	 echo "cdo -outputtab,date,time,lon,lat,value -remapnn,"lon=${lon}_lat=${lat}" -setgridtype,lonlat ${path_tmp}/a2.nc > $path_out/tmp2m_hor_${cit}_${a_aux}${m_aux}${d_aux}${h_aux}_03d.txt"
	 
	 cdo -outputtab,date,time,lon,lat,value -remapnn,"lon=${lon}_lat=${lat}" -setgridtype,lonlat ${path_tmp}/a2.nc > $path_out/tmp2m_hor_${cit}_${a_aux}${m_aux}${d_aux}${h_aux}_03d.txt
	 
	 
#	 cdo -outputtab,date,time,lon,lat,value -remapnn,"lon=${lon}_lat=${lat}" -setgrid,${path_tmp}/a2.nc ${path_tmp}/a2.nc > $path_out/tmp2m_hor_${cit}_${a_aux}${m_aux}${d_aux}${h_aux}_03d.txt
	 
	 
	  exit
	 echo "Arquivo Gerado Horario tmp2m p/ 03 dias  -> "$path_out/tmp2m_hor_${cit}_${a_aux}${m_aux}${d_aux}${h_aux}_07d.txt
	 #
	 cdo -outputtab,date,time,lon,lat,value -remapnn,"lon=${lon}_lat=${lat}" ${path_tmp}/a3.nc > $path_out/tmp2m_day_${cit}_${a_aux}${m_aux}${d_aux}${h_aux}_03d.txt
	 echo "Arquivo Gerado Diario tmp2m p/ 03 dias   -> "$path_out/tmp2m_day_${cit}_${a_aux}${m_aux}${d_aux}${h_aux}_03d.txt
	 #
	 cdo -outputtab,date,time,lon,lat,value -remapnn,"lon=${lon}_lat=${lat}" ${path_tmp}/c2.nc > $path_out/prec_hor_${cit}_${a_aux}${m_aux}${d_aux}${h_aux}_03d.txt
	 echo "Arquivo Gerado Horario prec p/ 03 dias  -> "$path_out/prec_hor_${cit}_${ai}${m_aux}${d_aux}${h_aux}_03d.txt
	 #
	 cdo -outputtab,date,time,lon,lat,value -remapnn,"lon=${lon}_lat=${lat}" ${path_tmp}/c3.nc > $path_out/prec_day_${cit}_${a_aux}${m_aux}${d_aux}${h_aux}_03d.txt
	 echo "Arquivo Gerado Diario prec p/ 03 dias   -> "$path_out/prec_day_${cit}_${a_aux}${m_aux}${d_aux}${h_aux}_03d.txt


	 for (( t = 0; t <= 4; t++ ))
	 do
	   fct=$(((t+1)*24))
	   data=`date -u --date="${a_aux}${m_aux}${d_aux} + $t days" +%Y%m%d%H`;# Linux
	   aa=`echo $data | awk '{ print substr($1,1,4)}'`
	   mm=`echo $data | awk '{ print substr($1,5,2)}'`
	   dd=`echo $data | awk '{ print substr($1,7,2)}'`
	   echo "FCT , Ano-Mes-Dia -> "${fct}" , "${aa}-${mm}-${dd}
	   mkdir -p ${path_cmp}/${aa}${mm}
	   mkdir -p ${path_cmp}/${aa}${mm}/f${fct}
	   grep "${aa}-${mm}-${dd}" $path_out/tmp2m_hor_${cit}_${a_aux}${m_aux}${d_aux}${h_aux}_03d.txt > ${path_cmp}/${aa}${mm}/f${fct}/tmp2m_gfs_hor_${cit}_f${fct}_${aa}${mm}${dd}.txt
	   grep "${aa}-${mm}-${dd}" $path_out/tmp2m_day_${cit}_${a_aux}${m_aux}${d_aux}${h_aux}_03d.txt > ${path_cmp}/${aa}${mm}/f${fct}/tmp2m_gfs_day_${cit}_f${fct}_${aa}${mm}${dd}.txt
	   grep "${aa}-${mm}-${dd}" $path_out/prec_hor_${cit}_${a_aux}${m_aux}${d_aux}${h_aux}_03d.txt > ${path_cmp}/${aa}${mm}/f${fct}/prec_gfs_hor_${cit}_f${fct}_${aa}${mm}${dd}.txt
	   grep "${aa}-${mm}-${dd}" $path_out/prec_day_${cit}_${a_aux}${m_aux}${d_aux}${h_aux}_03d.txt > ${path_cmp}/${aa}${mm}/f${fct}/prec_gfs_day_${cit}_f${fct}_${aa}${mm}${dd}.txt
	   

	 done  

	  #
	 
	#exit


	done
done


 

#
######################################################################
###	DELETA OS ARQUIVOS TEMPORTÃRIOS                           ###
######################################################################
#
rm -rf ${path_tmp}/*.nc
 
#exit


#cdo selname,tmp2m gfs.t00z.pgrb2.0p50.2025121500.f123_f384.nc b1.nc 




#
# faz o loop do perÃ­odo de dados
#
    
    
    exit
    
    #arq_dat=$path_dat/dados_INMET_${cod}_$yyyy$mmm.txt
    #

    
    echo "Arquivo Mensal Gerado -> "$arq_dat

    
    #
    # Inicia o Loop Das EstacÃµes
    #    
    # Inicia o Loop Das VariÃ¡veis (INMET,MERRA2). Para funcionar com as duas variÃ¡ves (INMET e MERRA2) j tem que ser <=2
    #     
#
done
#
# Apaga dados temporÃ¡rios
#
#rm -rf $path_dat/*.txt
#rm -rf nohup.out

