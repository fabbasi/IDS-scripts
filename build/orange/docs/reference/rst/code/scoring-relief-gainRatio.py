# Description: Ranking of features with two different measures (Relief and gain ratio)
# Category:    feature scoring
# Uses:        voting
# Referenced:  Orange.feature.html#scoring
# Classes:     Orange.feature.scoring.score_all, Orange.features.scoring.GainRatio

import Orange
voting = Orange.data.Table("voting")

print 'Relief GainRt Feature'
ma_def = Orange.feature.scoring.score_all(voting)
gr = Orange.feature.scoring.GainRatio()
ma_gr  = Orange.feature.scoring.score_all(voting, gr)
for i in range(5):
    print "%5.3f  %5.3f  %s" % (ma_def[i][1], ma_gr[i][1], ma_def[i][0])
