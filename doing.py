from jsplab.core.job import Job

if __name__ == "__main__":
    jobs=Job.make_jobs(2)
    for j in jobs:
        print(j)