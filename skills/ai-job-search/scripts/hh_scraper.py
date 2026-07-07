#!/usr/bin/env python3
"""
HH.ru Job Scraper

Searches vacancies on hh.ru via their public API.

Usage:
    python hh_scraper.py --query "Python разработчик" --area 1 --salary 150000 --limit 20

Parameters:
    --query: Search text (e.g., "Python разработчик")
    --area: City ID (1 = Москва, 2 = СПб, 113 = Россия)
    --salary: Minimum salary
    --only_with_salary: Only include jobs with salary listed
    --limit: Max results to return (default: 20)
    --output: Output JSON file (default: stdout)
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse


BASE_URL = "https://api.hh.ru/vacancies"

AREA_MAP = {
    "москва": 1,
    "moscow": 1,
    "спб": 2,
    "санкт-петербург": 2,
    "spb": 2,
    "stpetersburg": 2,
    "новосибирск": 4,
    "ekaterinburg": 3,
    "kazan": 88,
    "россия": 113,
    "russia": 113,
}


def search_vacancies(query, area=None, salary=None, only_with_salary=False, limit=20):
    params = {
        "text": query,
        "per_page": min(limit, 100),
        "page": 0,
    }
    if area:
        params["area"] = area
    if salary:
        params["salary"] = salary
        params["only_with_salary"] = "true" if only_with_salary else "false"

    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
    
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AI-Job-Search/1.0 (contact@example.com)",
            "Accept": "application/json",
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching from API: {e}", file=sys.stderr)
        return []

    results = []
    for item in data.get("items", []):
        salary_info = item.get("salary")
        salary_str = "Не указана"
        if salary_info:
            from_s = salary_info.get("from")
            to_s = salary_info.get("to")
            currency = salary_info.get("currency", "")
            gross = "gross" if salary_info.get("gross") else "net"
            if from_s and to_s:
                salary_str = f"{from_s:,} - {to_s:,} {currency} ({gross})"
            elif from_s:
                salary_str = f"От {from_s:,} {currency} ({gross})"
            elif to_s:
                salary_str = f"До {to_s:,} {currency} ({gross})"

        results.append({
            "id": item.get("id"),
            "title": item.get("name"),
            "company": item.get("employer", {}).get("name"),
            "url": item.get("alternate_url"),
            "salary": salary_str,
            "area": item.get("area", {}).get("name"),
            "published_at": item.get("published_at"),
            "snippet": item.get("snippet", {}).get("requirement", "").replace("<highlighttext>", "").replace("</highlighttext>", ""),
            "experience": item.get("experience", {}).get("name", "Не указан"),
            "employment": item.get("employment", {}).get("name", ""),
            "schedule": item.get("schedule", {}).get("name", ""),
        })

    return results[:limit]


def main():
    parser = argparse.ArgumentParser(description="Search hh.ru vacancies")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--area", type=str, help="Area ID or city name (e.g., 1, Moscow, Москва)")
    parser.add_argument("--salary", type=int, help="Minimum salary")
    parser.add_argument("--only-with-salary", action="store_true", help="Only vacancies with salary")
    parser.add_argument("--limit", type=int, default=20, help="Max results (default: 20)")
    parser.add_argument("--output", help="Output JSON file (default: stdout)")

    args = parser.parse_args()

    area_id = None
    if args.area:
        area_lower = args.area.lower().strip()
        if area_lower.isdigit():
            area_id = int(area_lower)
        else:
            area_id = AREA_MAP.get(area_lower)
            if not area_id:
                print(f"Warning: Unknown area '{args.area}'. Use area ID or known city name.", file=sys.stderr)

    results = search_vacancies(
        query=args.query,
        area=area_id,
        salary=args.salary,
        only_with_salary=args.only_with_salary,
        limit=args.limit,
    )

    output = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Saved {len(results)} vacancies to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
