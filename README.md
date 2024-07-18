# Technique Inference Engine

The goal of the Technique Inference Engine (TIE) project is to, given a small set of
observed MITRE ATT&CK techniques, predict the next most likely techniques.

**Table Of Contents:**

<!--
TODO The table of contents should include only h2-h6, NOT h1. The "Markdown All In One"
extension for VS Code will update the TOC automatically for you:
https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one
Set the extension's TOC:Levels setting to "2..6"
-->

- [Getting Started](#getting-started)
- [Getting Involved](#getting-involved)
- [Questions and Feedback](#questions-and-feedback)
- [How Do I Contribute?](#how-do-i-contribute)
- [Notice](#notice)

## Getting Started

To get started, clone the repository using git.  All required packages may be installed
via

`poetry build`

See https://python-poetry.org for details.

As the UI is still in the early stages of development, please utilize the provided
notebook main.ipynb in the models folder to play with the model during development.
All cells should be executed in order.  Feel free to play with the hyperparameters,
such as learning_rate, regularization_coefficient, gravity_coefficient, etc.

| Resource        | Description              |
| --------------- | ------------------------ |
| [Resource 1](#) | Description of resource. |
| [Resource 2](#) | Description of resource. |
| [Resource 3](#) | Description of resource. |

## Getting Involved

<!-- TODO Add some bullets telling users how to get involved. -->

There are several ways that you can get involved with this project and help
advance threat-informed defense:

- **Way to get involved 1.** Lorem ipsum dolor sit amet, consectetur adipiscing elit,
  sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
- **Way to get involved 2.** Ut enim ad minim veniam, quis nostrud exercitation ullamco
  laboris nisi ut aliquip ex ea commodo consequat.
- **Way to get involved 3.** Duis aute irure dolor in reprehenderit in voluptate velit
  esse cillum dolore eu fugiat nulla pariatur.

## Questions and Feedback

Please submit issues for any technical questions/concerns or contact
[ctid@mitre-engenuity.org](mailto:ctid@mitre-engenuity.org?subject=Question%20about%20technique-inference-engine)
directly for more general inquiries.

Also see the guidance for contributors if are you interested in contributing or simply
reporting issues.

## How Do I Contribute?

We welcome your feedback and contributions to help advance
Technique Inference Engine. Please see the guidance for contributors if are you
interested in [contributing or simply reporting issues.](/CONTRIBUTING.md)

Please submit
[issues](https://github.com/center-for-threat-informed-defense/technique-inference-engine/issues) for
any technical questions/concerns or contact
[ctid@mitre-engenuity.org](mailto:ctid@mitre-engenuity.org?subject=subject=Question%20about%20technique-inference-engine)
directly for more general inquiries.

## Notice

<!-- TODO Add PRS prior to publication. -->

Copyright 2023 MITRE Engenuity. Approved for public release. Document number REPLACE_WITH_PRS_NUMBER

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the specific language governing
permissions and limitations under the License.
