(function() {{
	const logLevels = ['log', 'warn', 'error'];
	logLevels.forEach(level => {{
		const original = console[level];
		console[level] = function(...args) {{
			original.apply(console, args);
			fetch('http://localhost:{FLASK_PORT}/console_log', {{
				method: 'POST',
				headers: {{ 'Content-Type': 'application/json' }},
				body: JSON.stringify({{ level, message: args }})
			}}).catch(error => original('Failed to send log:', error));
		}};
	}});
	const targetNode = document.querySelector('div.chatbody');
	if (!targetNode) {{
		console.error('No targetNode found.');
		return;
	}}
	console.log('Observing targetNode:', targetNode);
	const config = {{ childList: true, subtree: true, characterData: true, characterDataOldValue: true }};
	const extractMessageText = (node) => {{
		let messageText = '';
		node.childNodes.forEach(child => {{
			if (child.nodeType === Node.TEXT_NODE) {{
				messageText += child.textContent.replace(/\\s+/g, ' ');
			}} else if (child.nodeType === Node.ELEMENT_NODE) {{
				if (child.tagName === 'IMG') {{
					let imgSrc = child.currentSrc || child.getAttribute('src');
					if (imgSrc) {{
						if (!imgSrc.startsWith('http')) {{
							imgSrc = `https://dlive.tv${{imgSrc}}`;
						}}
						messageText += ` :::${{imgSrc}}::: `;
					}}
				}} else {{
					messageText += extractMessageText(child);
				}}
			}}
		}});
		return messageText;
	}};
	const generateUniqueId = (index, text) => `${{index}}-${{text.trim().replace(/\\s+/g, '£££')}}`;
	const getCurrentDivIds = () => {{
		return Array.from(targetNode.querySelectorAll('div')).map((div, index) => generateUniqueId(index, extractMessageText(div)));
	}};
	let previousDivIds = getCurrentDivIds();
	const containsGiftEmoji = (node) => {{
		if (node.nodeType === Node.ELEMENT_NODE && node.classList.contains('gift-emoji')) {{
			return true;
		}}
		return Array.from(node.childNodes).some(child => containsGiftEmoji(child));
	}};
	const handleMessage = (nodes, isAdded, ignoreNewMessages) => {{
		if (ignoreNewMessages && isAdded) {{
			return;
		}}
		for (const node of nodes) {{
			if (node.nodeType === 1) {{ // Element nodes only
				const messageText = extractMessageText(node).trim();
				const parent = node.parentNode;
				if (parent) {{
					const uniqueId = generateUniqueId(Array.from(parent.children).indexOf(node), messageText);
					const isGift = containsGiftEmoji(node);
					if (isAdded) {{
						console.log('New message detected:', messageText, 'Is gift:', isGift);
						fetch('http://localhost:{FLASK_PORT}/new_message', {{
							method: 'POST',
							headers: {{ 'Content-Type': 'application/json' }},
							body: JSON.stringify({{ message: messageText, is_gift: isGift }})
						}}).then(response => response.text())
						.then(data => console.log('Response from server (new_message):', data))
						.catch(error => console.error('Error:', error));
					}}
				}}
			}}
		}}
	}};
	const callback = (mutationsList) => {{
		console.error('\\n\\n******************************************************\\n\\n');
		const currentDivIds = getCurrentDivIds();
		// Variable pour suivre si une suppression a été détectée
		let deletionDetected = false;
		let removedText = null;
		let isGift = null;
		// Détection du premier message supprimé uniquement
		const removedId = previousDivIds.find(id => !currentDivIds.includes(id));
		if (removedId) {{
			removedText = removedId.substring(removedId.indexOf('-') + 1).replace(/£££/g, ' ').replace(/\\s+/g, ' ').trim();
			isGift = removedText.includes(":::https://dlive.tv/img/gift_");
			console.log(' isGift  in  JS:', isGift);
			if (!isGift) {{
				console.log('Message removed:', removedText);
				deletionDetected = true;
				fetch('http://localhost:{FLASK_PORT}/remove_message', {{
					method: 'POST',
					headers: {{ 'Content-Type': 'application/json' }},
					body: JSON.stringify({{ message: removedText, is_gift: isGift }})
				}}).then(response => response.text())
				.then(data => console.log('Response from server (remove_message):', data))
				.catch(error => console.error('Error:', error));
			}} else {{
				console.log('Mutation detected type GIFT. Mostly an increased GIFT');
				fetch('http://localhost:{FLASK_PORT}/upgrade_gift', {{
					method: 'POST',
					headers: {{ 'Content-Type': 'application/json' }},
					body: JSON.stringify({{ old_message: removedText }})
				}}).then(response => response.text())
				.then(data => console.log('Response from server (new_message):', data))
				.catch(error => console.error('Error:', error));
			}}
		}} else {{
			for (const mutation of mutationsList) {{
				if (mutation.type === 'childList') {{
					console.log('Mutation detected type : childList');
					handleMessage(mutation.addedNodes, true, deletionDetected);
					break;
				}}
			}}
		}}
		previousDivIds = getCurrentDivIds();
	}};
	const observer = new MutationObserver(callback);
	observer.observe(targetNode, config);
	console.log('MutationObserver attached and observing:', targetNode);
}})();
