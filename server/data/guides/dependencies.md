This guide assumes you have Python installed.

## Clone the Repo

Download the environments repo from GitHub:

```
git clone https://github.com/Wung8/AIPlayground_Environments.git
```

Or download it as a ZIP from the GitHub page and extract it.

## Create a Virtual Environment

Open a terminal in the repo folder and run:

```
python -m venv venv
```

## Activate the Virtual Environment

On Windows:
```
venv\Scripts\activate
```

On Mac/Linux:
```
source venv/bin/activate
```

Your terminal prompt should now show `(venv)`.

## Install Dependencies

```
pip install -r requirements.txt
```

You're ready to write and test bots locally.
