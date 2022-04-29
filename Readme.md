# LookML Action: Zendesk Cloud Function

This action provides an example of executing a row level webhook-style action directly from Looker. Specifically we are calling the Zendesk api from Looker and allowing users, more importantly Support Team Managers, to post notes, tags, update tickets, directly from a Looker query.

The repo contains a few different directories and files:

## cloud_function:
> Directory with cloud function source code 

| File | Description |
|---|---|
| `main.py` | This is the main source code for the cloud function. It contains a zendesk helper class that authenticates to the zendesk api and provides that auth object to the various methods a Looker user can call: `Add Comment`, `Set Priority`, `Reopen Ticket`, `Set Tags`.|
| `requirements.txt` | Contains the dependencies used by this function. |

## .github/workflows:
> Workflow file for CI/CD of cloud function

| File | Description |
|---|---|
| `example-workflow.yml` | This is the github workflow yaml file for continuous integration and deployment of this function to GCP. You will need to set up a [workload identity provider in GCP](https://cloud.google.com/iam/docs/configuring-workload-identity-federation) and save the provider and service account email to the `WIF_PROVIDER` and `SA_EMAIL` variables in your repo's secrets. Additional runtime variables required in the `deploy-function` step are: `ZENDESK_INSTANCE`, `ZENDESK_USERNAME`, `ZENDESK_USERID`, & `ZENDESK_ACCESS_TOKEN`. Once the function is deployed an IAM policy is added to all public access to this function (*looker doesn't yet support GCP IAM roles so the function needs to be publicly accessible.*) |