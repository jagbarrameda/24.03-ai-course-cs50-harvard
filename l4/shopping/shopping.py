import csv
import sys
import time

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")

    # compareTime(y_test, predictions)


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    # Read data in from file
    evidence = []
    labels = []
    with open(filename) as f:
        reader = csv.reader(f)
        next(reader) # skip header
        for row in reader:
            evidence.append([
                int(row[0]),
                float(row[1]),
                int(row[2]),
                float(row[3]),
                int(row[4])] +
                [float(cell) for cell in row[5:10]] +
                # month
                [monthToInt(row[10])] +
                [int(cell) for cell in row[11:15]] +
                [1 if row[15] == "Returning_Visitor" else 0,
                1 if row[16] == "True" else 0]
            )
            labels.append(1 if row[17] == "Revenue" else 0)
    return (evidence, labels)

def monthToInt(month: str) -> int:
    if month=='Jan':
        return 0
    if month=='Feb':
        return 1
    if month=='Mar':
        return 2
    if month=='Apr':
        return 3
    if month=='May':
        return 4
    if month=='Jun':
        return 5
    if month=='Jul':
        return 6
    if month=='Aug':
        return 7
    if month=='Sep':
        return 8
    if month=='Oct':
        return 9
    if month=='Nov':
        return 10
    if month=='Dec':
        return 11
    return -1


def train_model(evidence, labels) -> KNeighborsClassifier:
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    truePositive = 0
    totalPositive = 0
    trueNegative = 0
    totalNegative = 0
    for i in range(len(labels)):
        if labels[i] == 1:
            totalPositive += 1
            if predictions[i] == 1:
                truePositive += 1
        if labels[i] == 0:
            totalNegative += 1
            if predictions[i] == 0:
                trueNegative += 1
    return (truePositive/totalPositive if totalPositive != 0 else 0, 
            trueNegative/totalNegative if totalNegative != 0 else 0)

def evaluate2(labels, predictions):
    truePositive = sum(1 for label, prediction in zip(labels, predictions) if label == 1 and prediction == 1)
    totalPositive = sum(1 for label in labels if label == 1)
    trueNegative = sum(1 for label, prediction in zip(labels, predictions) if label == 0 and prediction == 0)
    totalNegative = sum(1 for label in labels if label == 0)
    
    return (truePositive / totalPositive if totalPositive != 0 else 0, 
            trueNegative / totalNegative if totalNegative != 0 else 0)


def compareTime(labels, predictions):
    # Measure execution time for the original version
    start_time = time.time()
    evaluate(labels, predictions)
    original_time = time.time() - start_time
    print("Execution time for the original version:", original_time, "seconds")

    # Measure execution time for the simplified version
    start_time = time.time()
    evaluate2(labels, predictions)
    simplified_time = time.time() - start_time
    print("Execution time for the simplified version:", simplified_time, "seconds")

if __name__ == "__main__":
    main()
