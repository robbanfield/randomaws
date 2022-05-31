# Rotating on CLI

Ref Doc: https://docs.aws.amazon.com/cli/latest/reference/secretsmanager/update-secret-version-stage.html

```
aws secretsmanager put-secret-value --secret-id "sec" --version-stages "NEWVERSION" --secret-string "FUZZYBEAR"
aws secretsmanager list-secret-version-ids --secret-id "sec"
```

This should now list AWSCURRENT & FUZZYBEAR + any older ones

```
aws secretsmanager get-secret-value --secret-id "sec" --version-stages "NEWVERSION" 
```

Should return FUZZYBEAR 

Get relevant Secret IDs.
```
aws secretsmanager list-secret-version-ids --secret-id "sec"
```

TEST Using this label

Rotate to new version, note to update staging label AWSCURRENT, you must specify RemoveFromVersionId and  MoveToVersionId.
```
aws secretsmanager update-secret-version-stage --secret-id "sec" --version-stage AWSCURRENT --move-to-version-id <DESTINATION> --remove-from-version <OLD AWSCURRENT>
```
