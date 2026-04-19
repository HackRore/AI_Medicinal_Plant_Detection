import os
env_files = ['.env', 'backend/.env', 'backend/app/.env', '.env.local']
for f in env_files:
    if os.path.exists(f):
        try:
            content = open(f).read()
            has_supa = 'SUPABASE' in content.upper() or 'DATABASE_URL' in content.upper()
            has_api = 'NEXT_PUBLIC_API_URL' in content
            print(f'{f}: supabase={has_supa} api_url={has_api}')
        except Exception as e:
            print(f'{f}: Error reading {e}')
    else:
        print(f'{f}: MISSING')
