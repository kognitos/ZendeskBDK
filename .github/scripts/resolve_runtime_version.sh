#!/bin/bash

TARGET_TAG=$1
FULL_REPO=$2

if ! [[ "$FULL_REPO" == *".dkr.ecr."* && "$FULL_REPO" == *".amazonaws.com"* ]]; then
    echo "Provided repo <$FULL_REPO> does not seem to be a supported AWS ECR URL."
    exit 1
fi

is_semver() {
    local pattern="^[0-9]+\.[0-9]+\.[0-9]+$"
    if [[ $1 =~ $pattern ]]; then
        echo "true"
    else
        echo "false"
    fi
}

if ! [[ $(is_semver "$TAG") == "true" ]]; then
    REPO=$(echo $FULL_REPO | cut -d'/' -f 2-)
    TAGS=$(aws ecr list-images --repository-name ${REPO} --query 'imageIds[*].imageTag' --output text)
    TARGET_DIGEST=$(aws ecr describe-images --repository-name ${REPO} --image-ids imageTag=${TARGET_TAG} --query 'imageDetails[0].imageDigest' --output text)

    IFS=' '
    for TAG in $(echo $TAGS | sed "s/\t/ /g"); do
        if [[ "$TAG" != $TARGET_TAG && $(is_semver "$TAG") == "true" ]]; then
            DIGEST=$(aws ecr describe-images --repository-name ${REPO} --image-ids imageTag=${TAG} --query 'imageDetails[0].imageDigest' --output text)
            if [ "$DIGEST" == "$TARGET_DIGEST" ]; then
                semver=$TAG
                break
            fi
        fi
    done

    if [ -n "$semver" ]; then
        echo "Found a matching version: $semver"
        echo "semver=$semver" >> $GITHUB_OUTPUT
    else
        echo "No matching Semver found, using default: $TARGET_TAG"
        echo "semver=$TARGET_TAG" >> $GITHUB_OUTPUT
    fi
else
    echo "Provided tag is already a valid Semver: $TARGET_TAG"
    echo "semver=$TARGET_TAG" >> $GITHUB_OUTPUT
fi