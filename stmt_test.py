from sklearn import cross_validation
from sklearn import datasets
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import f1_score
from LLDA.llda import LLDAClassifier


def main():
    iris = datasets.load_iris()
    iris.data.shape, iris.target.shape
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(iris.data, iris.target, test_size=0.4,
                                                                         random_state=0)

    mlb = MultiLabelBinarizer()
    y_train = [[each] for each in y_train]
    y_train = mlb.fit_transform(y_train)

    llda = LLDAClassifier(alpha=0.5 / y_train.shape[1])
    llda.fit(X_train, y_train)
    result = mlb.fit_transform(llda.predict(X_test, assignment=True))
    y_test = mlb.fit_transform([[each] for each in y_test])

    score_macro = f1_score(y_test, result, average="macro")
    score_micro = f1_score(y_test, result, average="micro")
    print("F1_macro:{0}, F1_micro:{1}".format(score_macro, score_micro))


if __name__ == '__main__':
    main()