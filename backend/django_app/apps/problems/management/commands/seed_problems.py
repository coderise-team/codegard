from django.core.management.base import BaseCommand
from apps.problems.models import Problem, TestCase


PROBLEMS_DATA = [
    {
        "title": "Two Sum",
        "slug": "two-sum",
        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "difficulty": "easy",
        "topic": "arrays",
        "test_cases": [
            {"input": "[2,7,11,15]\n9", "output": "[0,1]", "is_visible": True},
            {"input": "[3,2,4]\n6", "output": "[1,2]", "is_visible": True},
            {"input": "[3,3]\n6", "output": "[0,1]", "is_visible": True},
            {"input": "[1,5,8,3]\n11", "output": "[2,3]", "is_visible": False},
            {"input": "[-1,-2,-3,-4,-5]\n-8", "output": "[2,4]", "is_visible": False},
        ]
    },
    {
        "title": "Reverse String",
        "slug": "reverse string",
        "description": "Write a function that reverses a string. The input string is given as an array of characters s. You must mutate the input array in-place with $O(1)$ extra memory. Do not allocate extra space for another array.",
        "difficulty": "easy",
        "topic": "string",
        "test_cases": [
            {"input": '["H","e","l","l","o"]', "output": '["o","l","l","e","H"]', "is_visible": True},
            {"input": '["A","b","c","b","a"]', "output": '["a","b","c","b","A"]', "is_visible": True},
            {"input": '["o"]', "output": '["o"]', "is_visible": True},
            {"input": '["2","!"," ","?","`"]', "output": '["`","?"," ","!","2"]', "is_visible": False},
            {"input": '["a","A","a","A","a"]', "output": '["a","A","a","A","a"]', "is_visible": False},
        ]
    },
    {
        "title": "Palindrome Number",
        "slug": "palindrome number",
        "description": "Given an integer x, return true if x is a palindrome, and false otherwise. An integer is a palindrome when it reads the same backward as forward. For example, 121 is a palindrome while 123 is not. Negative numbers are never palindromes.",
        "difficulty": "easy",
        "topic": "math",
        "test_cases": [
            {"input": "121", "output": "true", "is_visible": True},
            {"input": "-121", "output": "false", "is_visible": True},
            {"input": "10", "output": "false", "is_visible": True},
            {"input": "12321", "output": "true", "is_visible": False},
            {"input": "0", "output": "true", "is_visible": False},
        ]
    },
    {
        "title": "Contains Duplicate",
        "slug": "contains-duplicate",
        "description": "Given an integer array nums, return true if any value appears at least twice in the array, and return false if every element is distinct.",
        "difficulty": "easy",
        "topic": "arrays",
        "test_cases": [
            {"input": "[1,2,3,1]", "output": "true", "is_visible": True},
            {"input": "[1,2,3,4]", "output": "false", "is_visible": True},
            {"input": "[1,1,1,3,3,4,3,2,4,2]", "output": "true", "is_visible": True},
            {"input": "[1000,2000,3000,1000]", "output": "true", "is_visible": False},
            {"input": "[-1,-2,-3]", "output": "false", "is_visible": False},
        ]
    },
    {
        "title": "Valid Anagram",
        "slug": "valid-anagram",
        "description": "Given two strings s and t, return true if t is an anagram of s, and false otherwise.",
        "difficulty": "easy",
        "topic": "strings",
        "test_cases": [
            {"input": '"anagram"\n"nagaram"', "output": "true", "is_visible": True},
            {"input": '"rat"\n"car"', "output": "false", "is_visible": True},
            {"input": '"a"\n"a"', "output": "true", "is_visible": True},
            {"input": '"awesome"\n"emosewa"', "output": "true", "is_visible": False},
            {"input": '"hello"\n"world"', "output": "false", "is_visible": False},
        ]
    },
    {
        "title": "Fizz Buzz",
        "slug": "fizz-buzz",
        "description": "Given an integer n, return a string array answer where answer[i] is Fizz/Buzz/FizzBuzz based on divisibility by 3 and 5.",
        "difficulty": "easy",
        "topic": "math",
        "test_cases": [
            {"input": "3", "output": '["1","2","Fizz"]', "is_visible": True},
            {"input": "5", "output": '["1","2","Fizz","4","Buyz"]', "is_visible": True},
            {"input": "15", "output": '["1","2","Fizz","4","Buzz","Fizz","7","8","Fizz","Buzz","11","Fizz","13","14","FizzBuzz"]', "is_visible": True},
            {"input": "1", "output": '["1"]', "is_visible": False},
            {"input": "0", "output": "[]", "is_visible": False},
        ]
    },
    {
        "title": "Single Number",
        "slug": "single-number",
        "description": "Given a non-empty array of integers nums, every element appears twice except for one. Find that single one.",
        "difficulty": "easy",
        "topic": "arrays",
        "test_cases": [
            {"input": "[2,2,1]", "output": "1", "is_visible": True},
            {"input": "[4,1,2,1,2]", "output": "4", "is_visible": True},
            {"input": "[1]", "output": "1", "is_visible": True},
            {"input": "[9,5,9,3,5]", "output": "3", "is_visible": False},
            {"input": "[-1,-1,-2]", "output": "-2", "is_visible": False},
        ]
    },
    {
        "title": "3Sum",
        "slug": "3sum",
        "description": "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j != k and their sum equals 0.",
        "difficulty": "medium",
        "topic": "arrays",
        "test_cases": [
            {"input": "[-1,0,1,2,-1,-4]", "output": "[[-1,-1,2],[-1,0,1]]", "is_visible": True},
            {"input": "[0,1,1]", "output": "[]", "is_visible": True},
            {"input": "[0,0,0]", "output": "[[0,0,0]]", "is_visible": True},
            {"input": "[-2,0,1,1,2]", "output": "[[-2,0,2],[-2,1,1]]", "is_visible": False},
            {"input": "[1,2,-3,4]", "output": "[[-3,1,2]]", "is_visible": False},
        ]
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "slug": "longest-substring",
        "description": "Given a string s, find the length of the longest substring without repeating characters.",
        "difficulty": "medium",
        "topic": "strings",
        "test_cases": [
            {"input": '"abcabcbb"', "output": "3", "is_visible": True},
            {"input": '"bbbbb"', "output": "1", "is_visible": True},
            {"input": '"pwwkew"', "output": "3", "is_visible": True},
            {"input": '""', "output": "0", "is_visible": False},
            {"input": '"abcdefg"', "output": "7", "is_visible": False},
        ]
    },
    {
        "title": "Pow(x, n)",
        "slug": "powx-n",
        "description": "Implement pow(x, n), which calculates x raised to the power n (i.e., x^n).",
        "difficulty": "medium",
        "topic": "math",
        "test_cases": [
            {"input": "2.00000\n10", "output": "1024.00000", "is_visible": True},
            {"input": "2.10000\n3", "output": "9.26100", "is_visible": True},
            {"input": "2.00000\n-2", "output": "0.25000", "is_visible": True},
            {"input": "1.00000\n0", "output": "1.00000", "is_visible": False},
            {"input": "-2.00000\n3", "output": "-8.00000", "is_visible": False},
        ]
    },
    {
        "title": "Container With Most Water",
        "slug": "container-with-most-water",
        "description": "Find two lines that together with the x-axis form a container, such that the container contains the most water.",
        "difficulty": "medium",
        "topic": "arrays",
        "test_cases": [
            {"input": "[1,8,6,2,5,4,8,3,7]", "output": "49", "is_visible": True},
            {"input": "[1,1]", "output": "1", "is_visible": True},
            {"input": "[4,3,2,1,4]", "output": "16", "is_visible": True},
            {"input": "[1,2,1]", "output": "2", "is_visible": False},
            {"input": "[10,9,8,7,6,5,4,3,2,1]", "output": "25", "is_visible": False},
        ]
    },
    {
        "title": "Reverse Words in a String",
        "slug": "reverse-words",
        "description": "Given an input string s, reverse the order of the words.",
        "difficulty": "medium",
        "topic": "strings",
        "test_cases": [
            {"input": '"the sky is blue"', "output": '"blue is sky the"', "is_visible": True},
            {"input": '"  hello world  "', "output": '"world hello"', "is_visible": True},
            {"input": '"a good   example"', "output": '"example good a"', "is_visible": True},
            {"input": '"single"', "output": '"single"', "is_visible": False},
            {"input": '"  multi   space  test "', "output": '"test space multi"', "is_visible": False},
        ]
    },
    {
        "title": "Median of Two Sorted Arrays",
        "slug": "median-two-arrays",
        "description": "Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays.",
        "difficulty": "hard",
        "topic": "arrays",
        "test_cases": [
            {"input": "[1,3]\n[2]", "output": "2.00000", "is_visible": True},
            {"input": "[1,2]\n[3,4]", "output": "2.50000", "is_visible": True},
            {"input": "[0,0]\n[0,0]", "output": "0.00000", "is_visible": True},
            {"input": "[]\n[1]", "output": "1.00000", "is_visible": False},
            {"input": "[2]\n[]", "output": "2.00000", "is_visible": False},
        ]
    },
    {
        "title": "Regular Expression Matching",
        "slug": "regex-matching",
        "description": "Given an input string s and a pattern p, implement regular expression matching with support for '.' and '*'.",
        "difficulty": "hard",
        "topic": "strings",
        "test_cases": [
            {"input": '"aa"\n"a"', "output": "false", "is_visible": True},
            {"input": '"aa"\n"a*"', "output": "true", "is_visible": True},
            {"input": '"ab"\n".*"', "output": "true", "is_visible": True},
            {"input": '"aab"\n"c*a*b"', "output": "true", "is_visible": False},
            {"input": '"mississippi"\n"mis*is*p*"', "output": "false", "is_visible": False},
        ]
    },
    {
        "title": "Max Points on a Line",
        "slug": "max-points-line",
        "description": "Given an array of points where points[i] = [xi, yi] represents a point on the 2D plane, return the maximum number of points that lie on the same straight line.",
        "difficulty": "hard",
        "topic": "math",
        "test_cases": [
            {"input": "[[1,1],[2,2],[3,3]]", "output": "3", "is_visible": True},
            {"input": "[[1,1],[3,2],[5,3],[4,1],[2,3],[1,4]]", "output": "4", "is_visible": True},
            {"input": "[[0,0]]", "output": "1", "is_visible": True},
            {"input": "[[1,1],[1,1]]", "output": "2", "is_visible": False},
            {"input": "[[1,1],[2,2],[1,2],[2,1]]", "output": "2", "is_visible": False},
        ]
    }
]


class Command(BaseCommand):
    help = "Seeds the database with 15 initial problems and test cases"

    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding...")

        for data in PROBLEMS_DATA:
            problem, created = Problem.objects.update_or_create(
                title=data["title"],
                defaults={
                    "description": data["description"],
                    "difficulty": data["difficulty"],
                }
            )

            if created:
                self.stdout.write(f"Created problem: {problem.title}")
            else:
                self.stdout.write(f"Updated problem: {problem.title}")

            TestCase.objects.filter(problem=problem).delete()

            for tc in data["test_cases"]:
                TestCase.objects.create(
                    problem=problem,
                    input=tc["input"],
                    expected_output=tc["output"],
                    is_hidden=tc["is_visible"],
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded 15 problems and test cases!"))
