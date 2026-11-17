### assignment 2a: personal code project - workshop feedback analysis


# import
import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import seaborn as sns
import time


# directory setup
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJ_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(PROJ_DIR, "in")
OUT_DIR = os.path.join(PROJ_DIR, "out")


# define main function
def main():
    # get user input arguments
    args = get_args()
    # load data from csv
    raw = load_data(args.filename)
    # clean data
    df = clean_data(raw)
    # convert str responses to numerical
    df = convert_likert(df)
    # set timestamp for naming outputs
    ts = time.strftime("%Y%m%d_%H%M%S")
    # summarise likert ratings
    summarise_likert(df, ts)
    # visualise
    likert_cols = ["likert_ca", "likert_cda", "likert_conlang",
                   "likert_ai", "likert_brugbart", "likert_lingvistik"]
    interest_cols = ["interesse_lingvistik", "interesse_studie"]
    for col in likert_cols:
        visualise_likert(df, col, ts)
    for col in interest_cols:
        visualise_interest(df, col, ts)
    # export comments
    export_comments(df, ts)
    print("Bar charts, Likert summary, and comment list saved to /out!")


# define subfunctions
def get_args():
    # create argparser
    parser = argparse.ArgumentParser(description = "filename of .csv file")
    # define arguments
    parser.add_argument("--filename",
                        "-f",
                        type=str,
                        required = True,
                        help = "filename of .csv file")
    args = parser.parse_args()
    return args

def load_data(filename):
    # define full filepath
    filepath = os.path.join(DATA_DIR, filename)
    # check
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    # load semicolon csv as df with row 1 as header cos that's how surveyxact works
    df = pd.read_csv(filepath, sep = ";", header = 1, encoding = "utf-8")
    return df

def clean_data(df):
    # drop irrelevant columns
    irrelevant_cols = ["Overall Status"] + [col for col in df.columns if "Unnamed" in str(col)]
    df = df.drop(columns = irrelevant_cols, errors = "ignore")
    # rename relevant columns by using a dict of partial original col names as map
    # original col names have æøå which python does not handle well
    renaming_dict = {"uddannelse er du i gang med": "uddannelse",
                     "emnet for dagens workshop": "workshop_emne",
                     "jeg kan bruge": "likert_brugbart",
                     "samtaleanalyse": "likert_ca",
                     "kritisk diskursanalyse": "likert_cda",
                     "bygget op": "likert_conlang",
                     "sprogmodeller": "likert_ai",
                     "hvad lingvistik er": "likert_lingvistik",
                     "lingvistik generelt": "interesse_lingvistik",
                     "studere lingvistik": "interesse_studie",
                     "andre kommentarer": "kommentarer"}
    # rename columns if the keyword is found in the raw column name
    for col in df.columns:
        for old_keyphrase, new_name in renaming_dict.items():
            if old_keyphrase in col:
                df = df.rename(columns = {col: new_name})
                break
    return df

def convert_likert(df):
    # list likert columns
    likert_cols = ["likert_ca", "likert_cda", "likert_conlang",
                   "likert_ai", "likert_brugbart", "likert_lingvistik"]
    # dict for mapping numerical conversion
    likert_scale = {"Meget uenig": 1, "Uenig": 2, "Hverken eller": 3, "Enig": 4,
                    "Meget enig": 5, "Ved ikke": None}
    # loop through likert columns to create numerical version of each
    for col in likert_cols:
        num_col = f"num_{col}"
        df[num_col] = df[col].replace(likert_scale)
    return df

def summarise_likert(df, ts):
    # define dict to match num likert col names with human-friendly labels
    label_dict = {"num_likert_sa": "Samtaleanalyse",
                  "num_likert_kda": "Kritisk diskursanalyse",
                  "num_likert_conlang": "Sprogopbygning (conlangs)",
                  "num_likert_ai": "AI og LLMs",
                  "num_likert_brugbart": "Brugbart",
                  "num_likert_lingvistik": "Lingvistik generelt"}
    summary = []
    for col, label in label_dict.items():
        # only include columns in dataset and not empty
        if col in df.columns and not df[col].dropna().empty:
            summary.append({"Spørgsmål": label,
                            "Gennemsnit (1-5)": round(df[col].mean(), 2),
                            "Std. afvigelse": round(df[col].std(), 2),
                            "Antal svar (N)": int(df[col].count())})
    # exit if all columns empty
    if not summary:
        return
    # turn into df and save as tab-separated txt for easy word-pasteability
    df_summary = pd.DataFrame(summary)
    df_summary.to_csv((os.path.join(OUT_DIR, f"likert_gennemsnit_{ts}.txt")), sep = "\t", index = False)

def get_pcts(df, col, order):
    # count number of each response type
    counts = df[col].value_counts()
    # calculate percentage value for each response type
    pcts = df[col].value_counts(normalize = True) * 100
    # put in a neat table
    table = pd.DataFrame({"count": counts, "pct": pcts.round(1)}).reindex(order, fill_value = 0).reset_index(names = "response")
    return table

def visualise_likert(df, col, ts):
    # skip if column not in dataset or empty
    if col not in df.columns or df[col].dropna().empty:
        return
    # define response type order
    order = ["Meget enig", "Enig", "Hverken eller", "Uenig", "Meget uenig", "Ved ikke"]
    # get percentage value for each response type
    table = get_pcts(df, col, order)
    # create barplot
    plt.figure(figsize = (8, 5))
    ax = sns.barplot(data=table,
                     x = "pct",
                     y = "response",
                     palette = {"Meget enig": "#2ca02c", "Enig": "#98df8a",
                                "Hverken eller": "#f9e79f", "Uenig": "#ff9896",
                                "Meget uenig": "#d62728", "Ved ikke": "#7f7f7f"},
                     hue = "response",
                     legend = False)
    # remove top and right lines
    sns.despine()
    # set x-axis limits
    plt.xlim(0, 100)
    # add values to each bar
    labels = [f"{pct}% (N = {count})" for pct, count in zip(table["pct"], table["count"])]
    for container, label in zip(ax.containers, labels):
        ax.bar_label(container, labels = [label], padding = 5)
    # set title & labels
    if col == "likert_ca":
        title = "Jeg har lært noget om, hvad samtaleanalyse er og kan bruges til"
    elif col == "likert_cda":
        title = "Jeg har lært noget om, hvad kritisk diskursanalyse er og kan bruges til"
    elif col == "likert_conlang":
        title = "Jeg har lært noget om, hvordan sprog kan være bygget op på forskellige måder"
    elif col == "likert_ai":
        title = "Jeg har lært noget om, hvordan AI og store sprogmodeller fungerer"
    elif col == "likert_brugbart":
        title = "Jeg har lært noget, jeg kan bruge på den uddannelse, jeg er i gang med nu"
    elif col == "likert_lingvistik":
        title = "Jeg ved mere om, hvad lingvistik er og kan bruges til"
    plt.title(title,
              fontsize = 12,
              weight = "bold",
              pad = 15,
              wrap = True)
    plt.xlabel("Respondenter (%)", fontsize = 12)
    plt.ylabel("")
    # save to png
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, f"{col}_{ts}.png"), bbox_inches = "tight")
    plt.close()

def visualise_interest(df, col, ts):
    # define response type order
    order = ["Ja, meget", "Ja, lidt", "Nej", "Jeg var interesseret i forvejen"]
    # get percentage value for each response type
    table = get_pcts(df, col, order)
    # create barplot
    plt.figure(figsize = (8, 4))
    ax = sns.barplot(data = table,
                     x = "pct",
                     y = "response",
                     palette = {"Ja, meget": "#2ca02c", "Ja, lidt": "#98df8a", 
                                "Nej": "#d62728", "Jeg var interesseret i forvejen": "#7f7f7f"},
                     hue = "response",
                     legend = False)
    # remove top and right lines
    sns.despine()
    # set x-axis limits
    plt.xlim(0, 100)
    # add values to each bar
    labels = [f"{pct}% (N = {count})" for pct, count in zip(table["pct"], table["count"])]
    for container, label in zip(ax.containers, labels):
        ax.bar_label(container, labels = [label], padding = 5)
    # set title & labels
    if col == "interesse_lingvistik":
        title = "Har workshoppen eller oplægget gjort dig interesseret i hovedemnet eller lingvistik generelt?"
    elif col == "interesse_studie":
        title = "Har workshoppen eller oplægget gjort dig interesseret i at studere lingvistik på universitetet?"
    plt.title(title,
              fontsize = 12,
              weight = "bold",
              pad = 15,
              wrap = True)
    plt.xlabel("Respondenter (%)", fontsize = 12)
    plt.ylabel("")
    # save to png
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, f"{col}_{ts}.png"), bbox_inches = "tight")
    plt.close()

def export_comments(df, ts):
    # skip if comment col not in dataset or empty
    if "kommentarer" not in df.columns or df["kommentarer"].dropna().empty:
        return
    # drop missing values and strip whitespace
    comments = df["kommentarer"].dropna().astype(str).str.strip()
    # filter out empty strings if any are left by stripping whitespace
    comments = comments[comments != ""]
    # save to txt
    with open((os.path.join(OUT_DIR, f"kommentarer_{ts}.txt")), "w", encoding = "utf-8") as f:
        for number, comment in enumerate(comments, 1):
            f.write(f"{number}. {comment}\n\n")


# if script is run from terminal, execute main function
if __name__=="__main__":
    main() 