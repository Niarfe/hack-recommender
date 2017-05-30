#!/bin/bash
URL_APPENDER_VERS=1.11
CURRENT_RUN=$1
if [ "$CURRENT_RUN" == "" ] ; then
  CURRENT_RUN=`date +"%Y%m%d"`
fi
ROOT_DIR=$PWD

echo "URL_APPENDER_VERS:${URL_APPENDER_VERS}"
echo "CURRENT_RUN=${CURRENT_RUN}"
echo "ROOT_DIR=${ROOT_DIR}"
echo -n "hit enter"
read


# ************************************************************************
# PREPERATION
# ************************************************************************
function prep {
echo "PREP ********************************"
  ## Get date of last delivered, by taking the name of the directory from nas location.
  MOST_RECENT=`find /nas/data/matcher/urls/  -name "companies_for_url*.zip" -exec ls -l {} \; | sed -e "s/^.*urls.//" | sort | sed -e "s/\/$//"|tail -1 | sed -e "s/.input.*//"`
  mkdir ${MOST_RECENT}

  ## find the last run files on s3
  LAST_RUN=`aws s3 ls s3://hg-url-appender/${URL_APPENDER_VERS}/20 |grep PRE | sed -e "s/^.*PRE //" | sed -e "s/\/$//"|tail -1`
  echo -n " Copy the /nas/data/matcher/urls/${MOST_RECENT}/input/companies_for_url.txt.zip from NAS (y/N)"
  read -t 10 confirm
  if [ "$confirm" == "y" ]; then
    cp -v /nas/data/matcher/urls/${MOST_RECENT}/input/companies_for_url.txt.zip ${MOST_RECENT}

    ## PREPARE to Import it into db-master to generate search requests
    echo " PREPARE to Import it into db-master to generate search requests"
    cd $MOST_RECENT

    unzip companies_for_url.txt.zip

      ### Trim off the header
      echo "Trim off the header"
      tail -n +2 companies_for_url.txt > companies.csv
      echo "bzip2 -v companies.csv"
      bzip2 -v companies.csv
      echo

    flushStdin;
    ### Make working directory
    mkdir -vp ${URL_APPENDER_VERS}/${CURRENT_RUN}/input/

    ### copy the input files master input directory s3://hg-url-appender/${URL_APPENDER_VERS}/input/
    echo -n "Copy the input files master input directory s3://hg-url-appender/${URL_APPENDER_VERS}/input/ (y/N) (10secs)"
    read -t 10 confirm
    if [ "$confirm" == "y" ]; then
      aws s3 sync s3://hg-url-appender/${URL_APPENDER_VERS}/input/ ${URL_APPENDER_VERS}/${CURRENT_RUN}/input/
    fi

    ### copy the companies.csv.bz2 last so that it overwrites
    mv -v companies.csv.bz2 ${URL_APPENDER_VERS}/${CURRENT_RUN}/input/

    ### copy all of it up to S3
    echo -n "Copy all of it up to S3 ${URL_APPENDER_VERS}/${CURRENT_RUN}/input =>  s3://hg-url-appender/${URL_APPENDER_VERS}/${CURRENT_RUN}/input (Y/n)"
    read -t 10 confirm
    if [ "$confirm" == "" ]; then confirm="y"; fi
    if [ "$confirm" == "y" ]; then
      echo "aws s3 sync ${URL_APPENDER_VERS}/${CURRENT_RUN}/input s3://hg-url-appender/${URL_APPENDER_VERS}/${CURRENT_RUN}/input "
      aws s3 sync ${URL_APPENDER_VERS}/${CURRENT_RUN}/input s3://hg-url-appender/${URL_APPENDER_VERS}/${CURRENT_RUN}/input
    fi


    echo
    echo "At this point s3://hg-url-appender/${URL_APPENDER_VERS}/${CURRENT_RUN}/input should have all the files"
    aws s3 ls s3://hg-url-appender/${URL_APPENDER_VERS}/${CURRENT_RUN}/input/

  fi
    echo
    echo -n "prep done - hit enter"
    read
}

# ************************************************************************
# RUN THE IMPORTER
# ************************************************************************
function importer {

  echo "IMPORTER ********************************"
  cd ${ROOT_DIR}
  touch nohup.out

  ## Inserts files from the s3://hg-url-appender/${URL_APPENDER_VERS}/${CURRENT_RUN}/input into tables on db-master
  echo "Inserts files from the s3://hg-url-appender/${URL_APPENDER_VERS}/${CURRENT_RUN}/input into tables on db-master"
  echo -n "Do you want to do this? (y/N) "
  read confirm

  if [ "$confirm" != "y" ]; then
     echo "skipping importer "
     return
  fi

  tail -f nohup.out &

  nohup java -jar url-appender.jar -r ${CURRENT_RUN} -s 1
  echo -n "importer done - hit enter"
  read
}

# ************************************************************************
# GENERATE DOWNLOAD REQUESTS
# ************************************************************************
function generate_download_requests {
echo "GENERATE_DOWNLOAD_REQUESTS  ********************************"
  cd ${ROOT_DIR}
  ## query db-master for new download requests
  echo "Query db-master for new download requests"
  mysql --defaults-file=${ROOT_DIR}/db-master.conf url_appender --skip-column-names -e "select search_text, market from searches where selected_at is not null;" > ${MOST_RECENT}/download-requests.csv
  cd ${MOST_RECENT}

  ## Convert csv to json
  echo "Convert csv to json "
  cat download-requests.csv | awk -F"\t" '{ print "{\"t\":\""$1"\",\"m\":\""$2"\"}" }' > download-requests.json

  ## Now split the file into 100,000 line files.
  ## This command will not work on MACs... only on ubuntu machines
  ## split
  ##   -a 5 (5 character suffix)
  ##   -d  (create numeric suffix)
  ##   --lines 100000
 ##   --additional-suffix=.json (will add .json to end of split filename)
  ##   download-requests.json (source file)
  ##   url-appender-${CURRENT_RUN}-part- (basename for split file)

  echo "Now split the file into 100,000 line files."
  split --verbose -a 5 -d --lines=100000 --additional-suffix=.json download-requests.json url-appender-${CURRENT_RUN}-part-

echo
echo
ls ${ROOT_DIR}/${MOST_RECENT}
echo -n "check for the existance of split files in ${ROOT_DIR}/${MOST_RECENT} (hit enter)"
read
:w
  ## bz2 the split files
  bzip2 -v url-appender-${CURRENT_RUN}-part-*.json

  ## make the directory structure for the hg-web-search tree
  mkdir -vp download/requests/url-appender-${CURRENT_RUN}

  ## move the bz2-ed split files into the tree sturcture
  mv -v url-appender-${CURRENT_RUN}-part-*.json*.bz2 download/requests/url-appender-${CURRENT_RUN}

echo -n "done with generate_download_requests - hit enter"
read

}

function upload_download_requests {

  cd ${ROOT_DIR}/${MOST_RECENT}
  pwd

  ## now upload to s3. This will fire off the requestDownloadWebSearches Lambda
  ## which will write each row to Kinesis: web-search-download-requests
  ## This will trigger downloadWebSearch Lambda
  ## reads rows off of Kinesis
  ## Makes Cognitive API call
  ##Saves results in s3://hg-raw-docs/url/search-results-v2

  echo "now upload to s3. This will fire off the requestDownloadWebSearches Lambda"
  echo "which will write each row to Kinesis: web-search-download-requests"
  echo "This will trigger downloadWebSearch Lambda"
  echo "reads rows off of Kinesis "
  echo "Makes Cognitive API call"
  echo "Saves results in s3://hg-raw-docs/url/search-results-v2"

  echo " **** THIS WILL CAUSE THE WEB SEARCH TO START ****"
  echo " ****      THIS WILL TAKE A LONG TIME         ****"
  echo
  echo -n " ARE YOU SURE YOU WANT TO DO THIS?!!!!!!! (y/N)"
  read confirm

  if [ "$confirm" != "y" ]; then
     echo "skipping upload_download_requests"
     return
  fi


  ## ####################################### ##
  ##             BE AWARE!!!!                ##
  ## ####################################### ##

  ## You would think that you can just copy all the split files up.

  ## ####################################### ##
  ##           BUT YOU CAN'T!!!!             ##
  ## ####################################### ##

  ## This will cause an error overloading the Kinesis Stream...
  ## You have to meter them out!!

  for i in download/requests/url-appender-${CURRENT_RUN}/*.bz2
  do
    aws s3 cp $i s3://hg-web-search/$i --dryrun
echo -n "hit enter"
read
    aws s3 cp $i s3://hg-web-search/$i
    sleep 300 ## wait 5 minutes between uploads so we don't overload the Kinesis Stream
  done

echo -n "done with upload_download_requests - hit enter"
read
}

function create_download_requests {
echo "CREATE_DOWNLOAD_REQUESTS  ********************************"
read -t 5

  cd ${ROOT_DIR}/${MOST_RECENT}

  ## splits the ${ROOT_DIR}/${MOST_RECENT}/download-requests.json into 1000 line files
  echo "Splits the ${ROOT_DIR}/${MOST_RECENT}/download-requests.json into 1000 line files"
  mkdir -vp parse/requests/url-appender-${CURRENT_RUN}
  rm -v parse/requests/url-appender-${CURRENT_RUN}/*
  cd parse/requests/url-appender-${CURRENT_RUN}

  ## Now split the file into 1000 line files.
  ## This command will not work on MACs... only on ubuntu machines
  ## split
  ##   -a 4 (4 character suffix)
  ##   -d  (create numeric suffix)
  ##   --lines 1000
  ##   --additional-suffix=.json (will add .json to end of split filename)
  ##   ${ROOT_DIR}/${MOST_RECENT}/download-requests.json (source file)
  ##   url-appender-${CURRENT_RUN}-part- (basename for split file)

  echo "Now split the ${ROOT_DIR}/${MOST_RECENT}/download-requests.json into 1000 line files."
  split -a 4 -d --lines 1000 --additional-suffix=.json ${ROOT_DIR}/${MOST_RECENT}/download-requests.json url-appender-${CURRENT_RUN}-part-

echo
echo "check for the existance of split files in ${ROOT_DIR}/${MOST_RECENT}/parse/requests/url-appender-${CURRENT_RUN}"
echo
ls ${ROOT_DIR}/${MOST_RECENT}/parse/requests/url-appender-${CURRENT_RUN}/
wc -l ${ROOT_DIR}/${MOST_RECENT}/download-requests.json
cat ${ROOT_DIR}/${MOST_RECENT}/parse/requests/url-appender-${CURRENT_RUN}/url-appender*part*.json | wc -l

echo -n "hit enter"
read
  ## bz2 the split files
  echo "bz2 the split files"
  bzip2 -v url-appender-${CURRENT_RUN}-part-*.json
  bzcat url-appender-${CURRENT_RUN}-part-*.json.bz2 | wc -l

echo "Done with CREATE_DOWNLOAD_REQUESTS  (hit enter) ********************************"
read
}


function upload_parse_requests {
  echo "UPLOAD_PARSE_REQUESTS  ********************************"
  ## Upload to  s3://hg-web-search/parse/requests/url-appender-${CURRENT_RUN}/
  ## This will fire off the parseWebSearches Lambda
  ## Lambda will read S3 files
  ## Downloads api responses
  ## Parses api responses
  ## Saves results in s3://hg-web-search/parse/responses/url-appender-${CURRENT_RUN}/

  echo "Upload to s3://hg-web-search/parse/requests/url-appender-${CURRENT_RUN}/"
  echo "This will fire off the parseWebSearches Lambda"
  echo "Lambda will read S3 files"
  echo "Downloads api responses"
  echo "Parses api responses"
  echo "Saves results in s3://hg-web-search/parse/responses/url-appender-${CURRENT_RUN}/"

  cd ${ROOT_DIR}/${MOST_RECENT}/parse/requests/url-appender-${CURRENT_RUN}
  pwd
  ls
  ls  url-appender-${CURRENT_RUN}-part-*.bz2

  echo " **** THIS WILL CAUSE THE PARSER TO START ****"
  echo " ****    THIS COULD TAKE A LONG TIME     ****"
  echo
  echo -n " ARE YOU SURE YOU WANT TO DO THIS?!!!!!!! (y/N)"
  read confirm

  if [ "$confirm" != "y" ]; then
     echo "skipping upload_parse_requests"
     return
  fi

  ## ok now we have to meter out the uploads so we don't overload anything

  for hundreds in {00..04}; do
    for tens in {00..49}; do
      for file in `ls  url-appender-${CURRENT_RUN}-part-${hundreds}${tens}*.bz2`; do
	aws s3 cp $file s3://hg-web-search/parse/requests/url-appender-${CURRENT_RUN}/$file
      done
    done
    sleep 60;
    for tens in {50..99}; do
      for file in `ls  url-appender-${CURRENT_RUN}-part-${hundreds}${tens}*.bz2`; do
	aws s3 cp $file s3://hg-web-search/parse/requests/url-appender-${CURRENT_RUN}/$file
      done
    done
    sleep 60;
  done
echo "DONE UPLOAD_PARSE_REQUESTS  ********************************"
echo "OK WAIT FOR THE parseWebSearches Lambda to finish"
echo "Saves results in s3://hg-web-search/parse/responses/url-appender-${CURRENT_RUN}/"

}

function download_parse_responses {
echo "DOWNLOAD_PARSE_RESPONSES ***********************************"
cd ${ROOT_DIR}/${MOST_RECENT}
echo " aws copy down"
mkdir -vp parse/responses/url-appender-${CURRENT_RUN}
rm parse/responses/url-appender-${CURRENT_RUN}/*
echo "aws s3 sync s3://hg-web-search/parse/responses/url-appender-${CURRENT_RUN}/ parse/responses/url-appender-${CURRENT_RUN} "
aws s3 sync s3://hg-web-search/parse/responses/url-appender-${CURRENT_RUN}/ parse/responses/url-appender-${CURRENT_RUN}

REQ_WC=`bzcat parse/requests/url-appender-${CURRENT_RUN}/*.bz2 | wc -l`
RESP_WC=`bzcat parse/responses/url-appender-${CURRENT_RUN}/*.bz2 | wc -l`

echo " verify the line count of the requests match the line count of the responses"
if [ $REQ_WC -ne $RESP_WC ]; then
  echo "Parse Requests(${REQ_WC}) do not match Responses(${RESP_WC})"
  echo -n "continue? (y/N)"
  read confirm
  if [ "${confirm}" != "y" ]; then
	return
  fi
fi

  cd parse/responses/url-appender-${CURRENT_RUN}
  rm parse-responses.json.bz2
  echo " then concat all the responses*.bz2 into a single bz2 file"
  cat *.bz2 >     parse-responses.json.bz2
  echo " bzip2 -t parse-responses.json.bz2"
  bzip2 -t parse-responses.json.bz2

  CAT_WC=`bzcat parse-responses.json.bz2 | wc -l`

  if [ $CAT_WC -ne $RESP_WC ]; then
    echo "parse-responses.json.bz2 ($CAT_WC) does not match total responses ($RESP_WC)"
    return
  fi
  echo " aws s3 cp parse-responses.json.bz2 s3://hg-url-appender/1.11/${CURRENT_RUN}/input/web_search_parse_responses.json.bz2"
  aws s3 cp parse-responses.json.bz2 s3://hg-url-appender/1.11/${CURRENT_RUN}/input/web_search_parse_responses.json.bz2
}

function flushStdin {
  while(true); do
    read -t 0.5 foo
    if [ $? > 0 ]; then return; fi
  done
}

function cleaner {
cd $ROOT_DIR
  echo "RESULTS CLEANER *****************"
  touch nohup.out
  tail -f nohup.out&
  nohup java -jar url-appender.jar -r ${CURRENT_RUN} -s 3

  echo "DONE RESULTS CLEANER (hit enter) *****************"
read
}

function candidator {
cd $ROOT_DIR
  echo "RESULTS CANDIDATOR *****************"
  touch nohup.out
  tail -f nohup.out&
  nohup java -jar url-appender.jar -r ${CURRENT_RUN} -s 4

  echo "DONE RESULTS CANDIDATOR (hit enter) *****************"
read
}

function scorer {
cd $ROOT_DIR
  echo "SCORER *****************"
  touch nohup.out
  tail -f nohup.out&
  nohup java -jar url-appender-1.11.999.jar -r ${CURRENT_RUN} -s 7

  echo "DONE SCORER *****************"
}

function chooser {
cd $ROOT_DIR
  echo "CHOOSER *****************"
  touch nohup.out
  tail -f nohup.out&
  nohup java -jar url-appender.jar -r ${CURRENT_RUN} -s 9

  echo "DONE CHOOSER *****************"
}



echo "starting url appender"
prep
#importer
#generate_download_requests
#upload_download_requests
create_download_requests
#upload_parse_requests
download_parse_responses
#cleaner
#candidator
#scorer
#chooser
#
#
#
#
#set +x