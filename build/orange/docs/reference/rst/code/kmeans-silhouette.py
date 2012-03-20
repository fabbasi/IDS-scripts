import Orange

voting = Orange.data.Table("voting")
# table = Orange.data.Table("iris")

for k in range(2, 8):
    km = Orange.clustering.kmeans.Clustering(voting, k, initialization=Orange.clustering.kmeans.init_diversity)
    score = Orange.clustering.kmeans.score_silhouette(km)
    print k, score

km = Orange.clustering.kmeans.Clustering(voting, 3, initialization=Orange.clustering.kmeans.init_diversity)
Orange.clustering.kmeans.plot_silhouette(km, "kmeans-silhouette.png")
