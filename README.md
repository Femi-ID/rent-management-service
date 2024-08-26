# RENT MANAGEMENT SERVICE (RENTPADDI)

## Project Overview

The Rent Management API serves as the backend for the creation, authorization of new users (Landlords and Tenants), payment of rent in the RENTPADDI application. It allows authenticated users to apply to be a potential tenant for available houses listed. Key features include landlord specific app for the property management, statistics view on the properties i.e amount generated, cost of maintenance, number of tenants, vacant properties available for rent among other features.

## Installation Instructions

### Prerequisites

Before setting up the project locally, ensure you have the following prerequisites installed:

- [Python](https://www.python.org/downloads/) (>=3.11.4)
- [Django](https://www.djangoproject.com/download/)
- [Django Rest Framework](https://www.django-rest-framework.org/#installation)
- A Database System (e.g., PostgreSQL, MySQL, SQLite) - [Django Database Installation](https://www.djangoproject.com/download/#database-installation)

### Installation Steps

1. Clone the repository:

        git clone https://github.com/Femi-ID/rent-management-service.git


2. Set up a virtual environment:

        python3 -m venv venv


3. Activate your virtual environment:

        source venv\Scripts\activate


4. Install the Python dependencies:

        pip install -r requirements.txt


5. Configure the database settings in the `settings.py` file according to your chosen database system.


7. Apply migrations to create the database schema:
        
        python manage.py makemigrations

        python manage.py migrate


8. Create a superuser for administrative access:

        python manage.py createsuperuser


9. Start the development server:
 python manage.py runserver

The API should now be running locally at [http://localhost:8000/](http://localhost:8000/).


## Usage Instructions
>
> ### Authentication
>
>> To access most endpoints of the API, you need to authenticate the user. Use the Token-based (JWT) authentication.
>
>> This section of the app contains the logic for user authentication and authorization.
>> To view more details under this application check here > [users](https://github.com/Femi-ID/rent-management-service/tree/dev/users). 


> ### Payment Feature:
>
>> The endpoint here contains the logic and handles everything regarding the payment and transaction done on the app. We implemented paystack's API for this feature. The user-type (landlord) is expected to create a new plan for the tenant to subscribe to (example: weekly, monthly bi-annual, annual) depending on what they opt for. More details here > [payments](https://github.com/Femi-ID/rent-management-service/tree/dev/payments)


> ### Swagger Doc Feature:
>
>> The endpoint here implements swagger's feature to test each endpoint in the application with proper documentation. It is useful as its tests each request method with their required parameters. You prefix `/swagger` after the localhost url.



## Getting Started

To get started with the project, refer to the [Installation Instructions](#installation-instructions) and [Usage Instructions](#usage-instructions) sections. Familiarize yourself with the API endpoints by exploring the [API Documentation](#api-documentation) provided.

## Configuration

Configuration details can be found in the project's `settings.py` file. Make sure to configure the required environment variables or configuration files as needed. Additionally, if any API keys or secrets are required, they should be mentioned in this section.

## Contribution

We welcome contributions from the community. Please follow our [Contribution Guidelines](#contribution-guidelines) for information on how to contribute to the project. You can submit bug reports, feature requests, or pull requests following the outlined process. We recommend creating an issue or replying in a comment to let us know what you are working on first that way we don't overwrite each other.

#### Contribution Guidelines
1. Clone the repo git clone https://github.com/Femi-ID/rent-management-service.git
2. Open your terminal & set the origin branch: `git remote add femii https://github.com/prosper-20/tutcov-backend.git`
3. Pull origin `git pull dev`
4. Create a new branch for the task you were assigned to, e.g TicketNumber/(Feat/Bug/Fix/Chore)/Ticket-title : `git checkout -b ZA-001/Feat/Receipts`
5. After making changes, do `git add .` 
6. Commit your changes with a descriptive commit message : `git commit -m "your commit message"`.
7. To make sure there are no conflicts, run `git pull femii dev`.
8. Push changes to your new branch, run `git push -u femii feat-new-branch-name`.
9. Create a pull request to the dev branch not main/master.
10. Ensure to **DESCRIBE your pull request**.
11. If you've added code that should be tested, add some test examples.


## Coding Standards

The project follows specific coding standards outlined in our [Coding Style Guide](#coding-standards). We use linting and code formatting tools to maintain code quality.


## Merging
#### Under any circumstances should you merge a pull request on a specific branch to the dev or main branch

### _Commit CheatSheet_
|   Type   |         Meaning          | Description                                                                                                 |
|:--------:|:------------------------:|:------------------------------------------------------------------------------------------------------------|
|   feat   |         Features         | A new feature                                                                                               |
|   fix    |       Bug Fixes          | 	A bug fix                                                                                                  |
|   docs   |      Documentation       | 	Documentation only changes                                                                                 |
|  style   |          Styles          | Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc.)     |
| refactor |     Code Refactoring     | 	A code change that neither fixes a bug nor adds a feature                                                  |
|   perf   | Performance Improvements | 	A code change that improves performance                                                                    |
|   test   |          Tests           | Adding missing tests or correcting existing tests                                                           |
|  build   |          Builds          | Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)         |
|    ci    | Continuous Integrations  | Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs) |
|  chore   |          Chores          | Other changes that don't modify, backend or test files                                                      |
|  revert  |         Reverts          | Reverts a previous commit                                                                                   |

> **Sample Commit Messages**

* `chore: Update README file`:= `chore` is used because the commit didn't make any changes to the frontend or test folders in any way.

* `feat: Add plugin info endpoints`:= `feat` is used here because the feature was non-existent before the commit.
<!-- ## Testing and Quality Assurance

To ensure code quality, follow the instructions in the [Testing Guidelines](#testing-and-quality-assurance) for running tests and quality checks on the codebase. The project uses a testing framework, and details on the testing tools are provided. -->


## API Documentation (if applicable)

You can access the API documentation [here](#api-documentation) when the server is running. It provides comprehensive information on how to use the API endpoints.

## License Information

This project is open-source and is licensed under the [MIT License](LICENSE). For the full license text, please [click here](LICENSE).

[//]: # (## Contributors)

[//]: # ()
[//]: # (We acknowledge and appreciate the contributions of the following individuals to this project:)

[//]: # ()
[//]: # (- [name]&#40;mailto:name@gmail.com&#41; - GitHub Profile: [here]&#40;https://github.com/name&#41;)

## Project Roadmap (Optional)

Our project roadmap outlines future plans and enhancements for the project. It serves as a guide for potential contributors and collaborators. You can find the roadmap in the [ROADMAP.md](ROADMAP.md) file.

&copy; 2024 rentpaddi Application Backend.