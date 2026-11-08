# 1. Simple query

My manager ask a simple question to me.

Possibilities:
- Answer from based on my knowledge
- Answer can be found by looking into the code
- Answer can be found by looking into the documentation
- Question is not clear to me, need some follow up questions.

# 2. Card Implementation

My manager assigned a story task to me

Actions:
- Analyze the card.
- Clarify open questions if any
- Create an implementation plan
- Ask for plan approval from TL
- Start development using test driven development
- Write test,
- Make test fails
- Write implementation
- rerun test again
- Once implementation is done. run all tests
- Review code
- if there is any feedback,

- Minor feedback: implement then test then review again
- Major feedback: Plan again, fix tests first then implementation. run tests, review.
- Submit as done.


# Software engineer agent (orchestration)

## Query analyser agent.
- Analyze if query is simple query
- Analyze if query is a task
- Analyze if query is response for questions which asked to user.

## Query resolver (Orchestration)
- Figure out how can I respond to query.

### Response based on general knowledge
- Based on my understanding response to user for simple query
### Response by looking into the code
- look into the relevant codebase
- provide answer
### Response by looking into the documentation
- Look into the relevant document
- provide answer
### Asks questions to users for clarifications
- Summarize understanding.
- ask all questions to users.
- provide answers/suggestions/recommendations of your questions to user


## Card implementation

### Card analyzer
- Analyze card,
- provide a detailed summary of the card
- If something is not clear, create a list of open questions
- Try to use tools if we can get the answers from Simple query agent

### Task planner
- split tasks into simple and multiple tasks
- create a list of simple tasks
- Show tasks to user

### Wait for approval

### Start implement code using TDD
- write test first
- run the tests
- Fix source code
- run again
- max 20 loops

### Dev testing
- Run all tests
- If failing create feedback and send back to tasks planner

### Code review
- Review new changes
- If feedback, share to task planner

### Summarize
- summarize it

