#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Usage:
>>> python irap.py [-f inputfile] [-c]
where:
  inputfile is IRAP log filename to process (leave logfile blank to ask for selection)
  -c compress the log to a binary version for faster access later

Originally created Feb 2016
@author: B. Dewberry
"""

import argparse
import sys, os
import pdb
sys.path.append('..')
import lib
import pickle
import pprint as pp
import numpy as np
import matplotlib.pyplot as plt
#from matplotlib.patches import patches
from matplotlib.backends.backend_pdf import PdfPages
from pprint import pprint as pp

parser = argparse.ArgumentParser(description='IRAP logfile analysis')
parser.add_argument('-f','--ffn_in',help='input file')
parser.add_argument('-c','--compress',action='store_true',default=False)
myargs = parser.parse_args()

ffn_in = myargs.ffn_in
compress_flag = myargs.compress

# temporary override
#ffn_in = '/Volumes/Transcend/Data/IRAP/test run = 10 pii 975 864002.csv'
#ffn_in = '/Volumes/Transcend/Data/IRAP/test run = 10 pii 975 864002.pkl'
#compress_flag = False

import csv
pii_table = []
with open('qualify-table.csv','rb') as csvfile :
#    stuff = csv.reader(csvfile,delimiter=' ',quotechar='|')
    stuff = csv.reader(csvfile)
    for row in stuff :
        print ', '.join(row)
        if 'Pii' == row[0][:3] :
            pii_row = (row[0], row[1], row[2], row[3].lstrip(' '))
            pii_table.append(pii_row)
        elif 'Range Limit' == row[0] :
            range_limits = ( float(row[1]), float(row[2]) )
        elif 'SNR Limit' == row[0] :
            snr_limits = ( float(row[1]), float(row[2]) )
        elif 'Pass/Fail SNR' == row[0] :
            pass_fail_snr = float(row[1])

pii_array = np.array(pii_table,dtype=[('label','S10'),('low','f4'),('high','f4'),('color','S10')])
pp(pii_array)
pp(range_limits)
pp(snr_limits)
#pdb.set_trace()

ffn_in = '/Volumes/Transcend/Data/IRAP/test run = 10 pii 975 864002.pkl'
if not ffn_in :
    ffn_in = lib.query_file()

path,fn_in = os.path.split(ffn_in)
fn_main,fn_ext = os.path.splitext(fn_in)
fn_pkl = fn_main + '.pkl'
ffn_pkl = os.path.join(path,fn_pkl)

#pdb.set_trace()
if fn_ext == '.csv' :
#if not os.path.isfile(ffn_pkl) or compress_flag :
    D = lib.read_log(ffn_in)
    fh_pkl = open(ffn_pkl,'wb')
    pickle.dump(D,fh_pkl)
    fh_pkl.close()
    print 'Compressed data saved to ', ffn_pkl
else :
    D = pickle.load(open(ffn_pkl,'rb'))


def plot_ranges(RA,nodeID) :

    nodeID_mask = RA['rspID'] == nodeID

    t_vec = RA[nodeID_mask]['t_host']
    t0 = RA['t_host'][0]
    t_vec = t_vec - t0

    r_vec = RA[nodeID_mask]['rmeas']

    plt.plot(t_vec,r_vec,'b.')
    plt.grid(True)

def plot_stopwatch(RA,nodeID,color,low,high) :

    nodeID_mask = RA['rspID']==nodeID

    mask_pii_hi = RA[nodeID_mask]['t_stopwatch'] >= low
    mask_pii_hi = mask_pii_hi.ravel()

    mask_pii_low = RA[nodeID_mask]['t_stopwatch'] <= high
    mask_pii_low = mask_pii_low.ravel()

    mask_pii = np.logical_and(mask_pii_hi,mask_pii_low)

    t0 = RA['t_host'][0]
    t_vec = RA[nodeID_mask][mask_pii]['t_host'] - t0
    vpk_vec = RA[nodeID_mask][mask_pii]['vpeak']
    noise_vec = RA[nodeID_mask][mask_pii]['noise']
    snr_vec = 20.*np.log10(np.divide(vpk_vec,noise_vec))

    lineH, = plt.plot(t_vec,snr_vec,color,
            hold=True,label='%d-%d'%(low,high),
            linestyle='None',marker='o',markersize=8,
            markerfacecolor=color,markeredgecolor=color)
    plt.grid(True)

    return lineH

req_list = np.unique(D['RcmRanges']['reqID'])
rsp_list = np.unique(D['RcmRanges']['rspID'])
pii_list = np.unique(D['RcmRanges']['t_stopwatch'])

fn_pdf = fn_main + '.pdf'
ffn_pdf = os.path.join(path,fn_pdf)
pdf = PdfPages(ffn_pdf)

plt.ion()
rsp_list = [101]
for nodeID in rsp_list :

    RA = D['RcmRanges'].ravel()

    fig = plt.figure(figsize=(18,10))

    ## Range Subplot
    ax0 = plt.subplot(211)
    plot_ranges(RA,nodeID)
    plt.suptitle(fn_main,fontsize=14)
    plt.title('Responder: %d' % (nodeID),fontsize=14)
    plt.ylabel('Distance (m)',fontsize=14)
    if 'range_limits' in locals() :
        ax0.set_ylim(range_limits)

    ## SNR Subplot
    ax1 = plt.subplot(212)
    colors = ['red', 'limegreen', 'blue', 'magenta', 'cyan', 'gray']
    lineH = []
#    lineH = [plot_stopwatch(RA,nodeID,colors[0],7,9)]
    lineH = [plot_stopwatch(RA, nodeID, pii_array[0]['color'], pii_array[0]['low'], pii_array[0]['high'] )]
    lineH.append(plot_stopwatch(RA,nodeID,colors[1],12,14))
    lineH.append(plot_stopwatch(RA,nodeID,colors[2],20,21))
    lineH.append(plot_stopwatch(RA,nodeID,colors[3],66,67))
    plt.ylabel('SNR = 20*log10(Vpeak/noise)',fontsize=14)

    plt.legend(handles=lineH,bbox_to_anchor=(0.,1.03,1.,.102),
                mode='expand',ncol=len(lineH),fancybox=True,shadow=True)

    if 'snr_limits' in locals() :
        ax1.set_ylim(snr_limits)

    xmax = max(ax0.get_)
    ax0.set

    plt.draw()

    pdf.savefig()

pdf.close()

pdb.set_trace()
#raw_input('press any key to quit:')