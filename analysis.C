#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>


#define CN 64
#define startch 25
#define endch 30

bool debug = 0;
Float_t gain[] = {1040.26, 1148.56, 1103.742, 1115.02, 1036.44, 1085.66};

Float_t arr_sum(Float_t arr[], int n)
{
    Float_t  sum = 0; // initialize sum
 
    // Iterate through all elements
    // and add them to sum
    for (int i = 0; i < n; i++)
    sum += arr[i];
 
    return sum;
}

void writeIntegral(const char* logfilename){
	
	Float_t x,y,z;
	char filename[30];
	Float_t LY_adc[endch-startch+1];
	Float_t LY_nph[endch-startch+1];
	Float_t LY_tot_adc;
	Float_t LY_tot_nph;	

	FILE *f_in; 
	if((f_in = fopen(logfilename,"r"))==NULL){
		fprintf( stderr, "Error- Unable to open %s\n", logfilename);
		exit(-1);
	}
	printf("Open %s\n",logfilename);
	
	string out_filename = string(logfilename).substr(0,string(logfilename).size()-4) + string(".root");
	
	TFile* f_out = new TFile(out_filename.c_str(),"RECREATE");
	TTree *t_out = new TTree("t_out","t_out");
	t_out->Branch("x",&x);	
	t_out->Branch("y",&y);	
	t_out->Branch("z",&z);	
	t_out->Branch("LY_adc",&LY_adc,"LY_adc[6]/F");	
	t_out->Branch("LY_nph",&LY_nph,"LY_nph[6]/F");	
	t_out->Branch("LY_tot_adc",&LY_tot_adc);	
	t_out->Branch("LY_tot_nph",&LY_tot_nph);	

	char buffer[256];
	while(fgets(buffer,256,f_in)){
		sscanf(buffer,"%f %f %f %s",&x,&y,&z,filename);
		printf("x: %f y:%f z:%f fn:%s\n",x,y,z,filename);
		
		TString data_path("/data/3dscan/livio_converted/rlog_");
		

		TFile *f_light = new TFile(data_path + TString(filename) + TString(".root"),"READ");
		if(f_light==0){
			fprintf(stderr,"Error- Data file %s not found\n",filename);
			exit(-1);
		}
		TTree *tr = (TTree*)f_light->Get("rlog");
		
		for(int ch = 0; ch<(endch-startch+1); ch++){
			Double_t max_bin = tr->GetMaximum(Form("integral.ch%02d>>h_temp",ch+startch));
			tr->Draw(Form("integral.ch%02d>>h_temp(10000,0,max_bin)",ch+startch));
			TH1F *h_temp = (TH1F*)gDirectory->Get("h_temp");
			LY_adc[ch] = h_temp->GetMean();
			//if(debug) printf("%f\n",LY_adc[ch]);
			LY_nph[ch] = LY_adc[ch]/gain[ch];
		}
		LY_tot_adc = arr_sum(LY_adc,endch-startch+1);
		LY_tot_nph = arr_sum(LY_nph,endch-startch+1);
		f_out->cd();
		t_out->Fill();
		if(debug) printf("%f   %f\n",LY_tot_adc,LY_tot_nph);
	}
	t_out->Write("t_out",TObject::kOverwrite);
	f_out->Close();
}


