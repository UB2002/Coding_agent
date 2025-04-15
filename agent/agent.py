from ai_client import AIClient
from executor import Executor

def main():
    ai_client = AIClient()
    executor = Executor()

    task = input("Enter the task for the AI agent (e.g., 'Generate and run a Python script to print Hello, World!'): ")

    plan = None
    while True:
        if not plan:
            plan = ai_client.generate_plan(task)
        print("\nProposed Plan:")
        print(plan)

        while True:
            approval = input("\nApprove this plan? (y/n): ").lower()
            if approval in ["y", "n"]:
                break
            print("Please enter 'y' or 'n'.")
        if approval == "n":
            print("Plan rejected. Exiting.")
            return

        success = executor.execute_plan(plan)
        if not success:
            print("Execution encountered an error.")

        while True:
            result = input("\nWas the task successful? (y/n): ").lower()
            if result in ["y", "n"]:
                break
            print("Please enter 'y' or 'n'.")
        if result == "y":
            print("Task completed successfully. Exiting.")
            break
        else:
            error_reason = input("Why did the task fail? (Provide details): ")
            plan = ai_client.refine_plan(task, plan, error_reason)

if __name__ == "__main__":
    main()