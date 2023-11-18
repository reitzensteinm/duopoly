# Duopoly

Duopoly is a GPT-4 software developer. It's building itself, right from
the [second commit](https://github.com/reitzensteinm/duopoly/commit/7646e1be5a281e87d58ea995f694bf39d247d264).

### Aims

1) Be a virtual developer. All interaction happens over GitHub issues, Slack, etc.
2) Rapidly achieve liftoff. No human code allowed. 🚀🚀🚀

### Status

🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩 100% commits AI written last month
🟩🟩🟩🟩🟩🟩🟩🟩🟩🟥 97% commits AI written last three months
🟩🟩🟩🟩🟩🟩🟩🟩🟥🟥 84% commits AI written all time

**Last human commit: 10th September, 2023**

💰 OpenAI GPT-4 Turbo Cost: Approximately $2 per commit

- [x] Read GitHub Issues and create Pull Requests
- [x] First class support for Python tooling
- [x] Quality steps, including feedback from reflection, PyTest, PyLint and MyPy
- [x] Parallel execution
- [x] HTML Report Generation
- [ ] Respond to PR feedback
- [ ] Evals framework to track performance over time
- [ ] Precalculated code summarization for Retrieval Augmented Generation
- [ ] First class support for TypeScript/JavaScript tooling

### Getting Started

* **settings.py** contains GitHub a list of repositories to check, and usernames to respond to
* Set ```GITHUB_API_KEY``` and ```OPENAI_API_KEY```
* Install requirements via ```pip install -r requirements.txt```
* Run Duopoly via ```run.sh``` helper, or ```python src/main.py```

### Contributing

**Duopoly will not accept human written PRs.**

To contribute to Duopoly, use Duopoly on Duopoly!