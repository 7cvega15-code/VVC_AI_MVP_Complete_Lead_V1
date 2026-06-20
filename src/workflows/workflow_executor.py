def execute_workflow(workflow):

    if workflow == "FULL_PROPOSAL":
        return "SHOW_PROPOSAL"

    elif workflow == "PRELIMINARY_PROPOSAL":
        return "SHOW_PROPOSAL_AND_QUESTIONS"

    else:
        return "SHOW_QUESTIONS_ONLY"