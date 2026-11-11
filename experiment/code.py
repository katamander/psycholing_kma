def remove_outliers(group):
    mean_rt = group["RT"].mean()
    std_rt = group["RT"].std()
    
    # filter out rows outside 2.5 standard deviations
    lower_bound = mean_rt - (2.5 * std_rt)
    upper_bound = mean_rt + (2.5 * std_rt)
    
    return group[(group["RT"] >= lower_bound) & (group["RT"] <= upper_bound)]

df_clean = df.groupby(["Subject", "Duration", "Gram"], group_keys=False).apply(remove_outliers)


# calculate hit and false alarm rates
grammatical_trials = df_clean[df_clean["Gram"] == 0]
ungrammatical_trials = df_clean[df_clean["Gram"] == 1]

hits = grammatical_trials.groupby(["Subject", "Duration"])["Accuracy"].mean().reset_index()
hits = hits.rename(columns={"Accuracy": "Hit_Rate"})

false_alarms = ungrammatical_trials.groupby(["Subject", "Duration"])["Accuracy"].apply(lambda x: (x == 0).mean()).reset_index()
false_alarms = false_alarms.rename(columns={"Accuracy": "FA_Rate"})

results = pd.merge(hits, false_alarms, on=["Subject", "Duration"])

results["Hit_Rate"] = np.clip(results["Hit_Rate"], 0.01, 0.99)
results["FA_Rate"] = np.clip(results["FA_Rate"], 0.01, 0.99)


# calculate average RT for all 4 response types
conditions = [(df_clean['Gram'] == 0) & (df_clean['Accuracy'] == 1),  # hit
              (df_clean['Gram'] == 0) & (df_clean['Accuracy'] == 0),  # miss
              (df_clean['Gram'] == 1) & (df_clean['Accuracy'] == 1),  # correct rejection
              (df_clean['Gram'] == 1) & (df_clean['Accuracy'] == 0)]  # false alarm

choices = ['RT_Hit', 'RT_Miss', 'RT_CR', 'RT_FA']

df_clean['Outcome'] = np.select(conditions, choices)

rt_means = df_clean.pivot_table(index=['Subject', 'Duration'],
                                columns='Outcome',
                                values='RT', 
                                aggfunc='mean').reset_index()

results = pd.merge(results, rt_means, on=['Subject', 'Duration'])

# calculate d' and c 
results["Z_Hit"] = norm.ppf(results["Hit_Rate"])
results["Z_FA"] = norm.ppf(results["FA_Rate"])

results["d_prime"] = results["Z_Hit"] - results["Z_FA"]

results["c_bias"] = -0.5 * (results["Z_Hit"] + results["Z_FA"])

# average scores by presentation duration across participants
final = results.groupby('Duration')[['d_prime', 'c_bias', 'RT_Hit', 'RT_Miss', 'RT_CR', 'RT_FA']].mean().reset_index()

# plot 1 - accuracy
results['CR_Rate'] = 1 - results['FA_Rate']
sns.set_theme(style="whitegrid")

plt.figure(figsize=(8, 5))

sns.pointplot(data=results, 
              x='Duration',
              y='Hit_Rate',
              color='royalblue', 
              markers='o', 
              scale=0.8,
              errorbar='se', 
              label='grammatical')

sns.pointplot(data=results, 
              x='Duration', 
              y='CR_Rate',
              color='indianred', 
              markers='o', 
              scale=0.8,
              errorbar='se', 
              label='ungrammatical')

plt.title("Evolution of Probability of Correct Responses")
plt.xlabel("Stimulus duration (ms)")
plt.ylabel("Probability correct")
plt.ylim(0.5, 0.9)
plt.legend()
plt.show()

# plot 2 - sensitivity
plt.figure(figsize=(6, 5))

sns.pointplot(data=results, 
              x='Duration', 
              y='d_prime',
              color='blue', 
              markers='o', 
              scale=0.8,
              errorbar='ci', 
              linestyles='')

plt.title("Evolution of Sensitivity (d')")
plt.xlabel("Stimulus duration (ms)")
plt.ylabel("Sensitivity (d')")
plt.ylim(0.5, 3.2)
plt.show()

# plot 3 - bias
plt.figure(figsize=(6, 5))

sns.pointplot(data=results, 
              x='Duration', 
              y='c_bias', 
              color='blue', 
              markers='o', 
              scale=0.8,
              errorbar='ci', 
              linestyles='')

plt.title("Evolution of Bias (c)")
plt.xlabel("Stimulus duration (ms)")
plt.ylabel("Bias (c)")
plt.ylim(-1.0, 1.0)
plt.axhline(0, color='gray', linestyle='--', alpha=0.7)
plt.show()
